"""
Security middleware and utilities for Executive Mind Matrix.
Includes rate limiting, CORS configuration, and security headers.
"""

from fastapi import Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Optional
from loguru import logger
import secrets
import time


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""

    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        return response


class APIKeyMiddleware(BaseHTTPMiddleware):
    """Validate API key for protected endpoints"""

    def __init__(self, app, api_key: Optional[str], api_key_header: str = "X-API-Key"):
        super().__init__(app)
        self.api_key = api_key
        self.api_key_header = api_key_header
        self.public_paths = ["/", "/health", "/metrics", "/docs", "/redoc", "/openapi.json"]

    async def dispatch(self, request: Request, call_next: Callable):
        # Skip API key check for public paths
        if request.url.path in self.public_paths or not self.api_key:
            return await call_next(request)

        # Check API key
        provided_key = request.headers.get(self.api_key_header)

        if not provided_key:
            logger.warning(f"Missing API key for {request.url.path} from {request.client.host}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": f"Missing {self.api_key_header} header"}
            )

        # Use constant-time comparison to prevent timing attacks
        if not secrets.compare_digest(provided_key, self.api_key):
            logger.warning(f"Invalid API key for {request.url.path} from {request.client.host}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid API key"}
            )

        return await call_next(request)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all incoming requests with timing information"""

    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()

        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent", "unknown")
            }
        )

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Log response
        logger.info(
            f"Response: {request.method} {request.url.path} - {response.status_code} ({duration:.3f}s)",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration": duration
            }
        )

        # Add timing header
        response.headers["X-Process-Time"] = str(duration)

        return response


def setup_cors(app, allowed_origins: list[str]):
    """
    Setup CORS middleware.

    Args:
        app: FastAPI application instance
        allowed_origins: List of allowed origins
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Process-Time"],
    )

    logger.info(f"CORS configured with origins: {allowed_origins}")


def setup_rate_limiting(app, rate_limit_per_minute: int = 60):
    """
    Setup rate limiting.

    Args:
        app: FastAPI application instance
        rate_limit_per_minute: Maximum requests per minute per IP

    Returns:
        Limiter instance
    """
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[f"{rate_limit_per_minute}/minute"],
        storage_uri="memory://",
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    logger.info(f"Rate limiting configured: {rate_limit_per_minute} requests/minute")

    return limiter


def setup_trusted_hosts(app, allowed_hosts: list[str]):
    """
    Setup trusted host middleware.

    Args:
        app: FastAPI application instance
        allowed_hosts: List of allowed host headers
    """
    if allowed_hosts and allowed_hosts != ["*"]:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=allowed_hosts
        )
        logger.info(f"Trusted hosts configured: {allowed_hosts}")


def generate_api_key() -> str:
    """
    Generate a secure random API key.

    Returns:
        A secure random API key
    """
    return secrets.token_urlsafe(32)


class CircuitBreaker:
    """
    Circuit breaker pattern for external API calls.
    Prevents cascading failures by stopping requests after too many failures.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
            expected_exception: Exception type to catch
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open

    def call(self, func: Callable, *args, **kwargs):
        """
        Execute function with circuit breaker protection.

        Args:
            func: Function to execute
            *args, **kwargs: Function arguments

        Returns:
            Function result

        Raises:
            HTTPException: When circuit is open
            Exception: Original exception when circuit is closed
        """
        if self.state == "open":
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = "half_open"
                logger.info("Circuit breaker entering half-open state")
            else:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Service temporarily unavailable (circuit breaker open)"
                )

        try:
            result = func(*args, **kwargs)

            # Success - reset or close circuit
            if self.state == "half_open":
                self.state = "closed"
                self.failure_count = 0
                logger.info("Circuit breaker closed after successful call")

            return result

        except self.expected_exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = "open"
                logger.error(
                    f"Circuit breaker opened after {self.failure_count} failures"
                )

            raise e

    def reset(self):
        """Manually reset circuit breaker"""
        self.failure_count = 0
        self.state = "closed"
        self.last_failure_time = None
        logger.info("Circuit breaker manually reset")

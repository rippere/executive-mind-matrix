#!/usr/bin/env python3

"""
Smoke test script for Executive Mind Matrix.
Runs basic health checks against a deployed instance.
"""

import asyncio
import httpx
import sys
import os
from typing import Dict, List, Tuple
from datetime import datetime


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


class SmokeTest:
    """Smoke test runner"""

    def __init__(self, base_url: str, api_key: str = None, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.results: List[Tuple[str, bool, str]] = []

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with optional API key"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "ExecutiveMindMatrix-SmokeTest/1.0"
        }

        if self.api_key:
            headers["X-API-Key"] = self.api_key

        return headers

    async def test_root_endpoint(self) -> bool:
        """Test the root endpoint"""
        test_name = "Root Endpoint (/)"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/",
                    headers=self._get_headers()
                )

                if response.status_code == 200:
                    data = response.json()

                    # Check required fields
                    if all(key in data for key in ["status", "service", "version"]):
                        if data["status"] == "running":
                            self.results.append((test_name, True, f"Status: {data['status']}"))
                            return True
                        else:
                            self.results.append((test_name, False, f"Status is '{data['status']}', expected 'running'"))
                            return False
                    else:
                        self.results.append((test_name, False, "Missing required fields in response"))
                        return False
                else:
                    self.results.append((test_name, False, f"HTTP {response.status_code}"))
                    return False

        except Exception as e:
            self.results.append((test_name, False, f"Error: {str(e)}"))
            return False

    async def test_health_endpoint(self) -> bool:
        """Test the health check endpoint"""
        test_name = "Health Endpoint (/health)"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/health",
                    headers=self._get_headers()
                )

                if response.status_code == 200:
                    data = response.json()

                    # Check required fields
                    if "status" in data and data["status"] == "healthy":
                        # Check databases configured
                        if "databases_configured" in data:
                            db_count = sum(data["databases_configured"].values())
                            self.results.append((test_name, True, f"Healthy, {db_count} databases configured"))
                            return True
                        else:
                            self.results.append((test_name, True, "Healthy"))
                            return True
                    else:
                        self.results.append((test_name, False, "Status is not 'healthy'"))
                        return False
                else:
                    self.results.append((test_name, False, f"HTTP {response.status_code}"))
                    return False

        except Exception as e:
            self.results.append((test_name, False, f"Error: {str(e)}"))
            return False

    async def test_metrics_endpoint(self) -> bool:
        """Test the Prometheus metrics endpoint"""
        test_name = "Metrics Endpoint (/metrics)"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/metrics",
                    headers=self._get_headers()
                )

                if response.status_code == 200:
                    content = response.text

                    # Check for Prometheus format
                    if "# HELP" in content and "# TYPE" in content:
                        metric_count = content.count("# TYPE")
                        self.results.append((test_name, True, f"{metric_count} metrics exposed"))
                        return True
                    else:
                        self.results.append((test_name, False, "Invalid Prometheus format"))
                        return False
                elif response.status_code == 404:
                    self.results.append((test_name, False, "Metrics endpoint not found (may not be enabled)"))
                    return False
                else:
                    self.results.append((test_name, False, f"HTTP {response.status_code}"))
                    return False

        except Exception as e:
            self.results.append((test_name, False, f"Error: {str(e)}"))
            return False

    async def test_docs_endpoint(self) -> bool:
        """Test the API documentation endpoint"""
        test_name = "API Docs (/docs)"

        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(
                    f"{self.base_url}/docs",
                    headers=self._get_headers()
                )

                if response.status_code == 200:
                    self.results.append((test_name, True, "Swagger UI accessible"))
                    return True
                else:
                    self.results.append((test_name, False, f"HTTP {response.status_code}"))
                    return False

        except Exception as e:
            self.results.append((test_name, False, f"Error: {str(e)}"))
            return False

    async def test_response_time(self) -> bool:
        """Test response time for root endpoint"""
        test_name = "Response Time"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                start_time = datetime.now()
                response = await client.get(
                    f"{self.base_url}/",
                    headers=self._get_headers()
                )
                end_time = datetime.now()

                response_time = (end_time - start_time).total_seconds() * 1000  # Convert to ms

                if response.status_code == 200:
                    if response_time < 1000:  # Less than 1 second
                        self.results.append((test_name, True, f"{response_time:.2f}ms"))
                        return True
                    else:
                        self.results.append((test_name, False, f"{response_time:.2f}ms (slow response)"))
                        return False
                else:
                    self.results.append((test_name, False, f"HTTP {response.status_code}"))
                    return False

        except Exception as e:
            self.results.append((test_name, False, f"Error: {str(e)}"))
            return False

    async def test_security_headers(self) -> bool:
        """Test that security headers are present"""
        test_name = "Security Headers"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/",
                    headers=self._get_headers()
                )

                security_headers = [
                    "X-Content-Type-Options",
                    "X-Frame-Options",
                    "X-XSS-Protection",
                ]

                missing_headers = []
                for header in security_headers:
                    if header not in response.headers:
                        missing_headers.append(header)

                if not missing_headers:
                    self.results.append((test_name, True, "All security headers present"))
                    return True
                else:
                    self.results.append((test_name, False, f"Missing: {', '.join(missing_headers)}"))
                    return False

        except Exception as e:
            self.results.append((test_name, False, f"Error: {str(e)}"))
            return False

    async def run_all_tests(self):
        """Run all smoke tests"""
        print(f"\n{Colors.BLUE}{'=' * 60}{Colors.NC}")
        print(f"{Colors.BLUE}Executive Mind Matrix - Smoke Tests{Colors.NC}")
        print(f"{Colors.BLUE}{'=' * 60}{Colors.NC}\n")
        print(f"Target: {self.base_url}")
        print(f"Timeout: {self.timeout}s\n")

        # Run tests
        tests = [
            self.test_root_endpoint(),
            self.test_health_endpoint(),
            self.test_response_time(),
            self.test_security_headers(),
            self.test_metrics_endpoint(),
            self.test_docs_endpoint(),
        ]

        await asyncio.gather(*tests, return_exceptions=True)

        # Print results
        print(f"{Colors.BLUE}Test Results:{Colors.NC}\n")

        passed = 0
        failed = 0

        for test_name, success, message in self.results:
            status = f"{Colors.GREEN}✓{Colors.NC}" if success else f"{Colors.RED}✗{Colors.NC}"
            print(f"  {status} {test_name}: {message}")

            if success:
                passed += 1
            else:
                failed += 1

        # Summary
        print(f"\n{Colors.BLUE}{'=' * 60}{Colors.NC}")
        print(f"Total: {passed + failed} tests")
        print(f"{Colors.GREEN}Passed: {passed}{Colors.NC}")

        if failed > 0:
            print(f"{Colors.RED}Failed: {failed}{Colors.NC}")
            print(f"\n{Colors.RED}Smoke tests failed!{Colors.NC}\n")
            return False
        else:
            print(f"\n{Colors.GREEN}All smoke tests passed!{Colors.NC}\n")
            return True


async def main():
    """Main entry point"""
    # Get configuration from environment or arguments
    base_url = os.environ.get('SMOKE_TEST_URL', 'http://localhost:8000')
    api_key = os.environ.get('API_KEY')
    timeout = int(os.environ.get('SMOKE_TEST_TIMEOUT', '30'))

    # Override with command line arguments if provided
    if len(sys.argv) > 1:
        base_url = sys.argv[1]

    if len(sys.argv) > 2:
        api_key = sys.argv[2]

    # Run tests
    smoke_test = SmokeTest(base_url, api_key, timeout)
    success = await smoke_test.run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())

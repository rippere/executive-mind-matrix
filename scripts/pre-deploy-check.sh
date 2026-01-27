#!/bin/bash

# Pre-deployment checklist script for Executive Mind Matrix
# This script validates the environment and configuration before deployment

set -e

echo "================================"
echo "Pre-Deployment Checklist"
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
        ERRORS=$((ERRORS + 1))
    fi
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
    WARNINGS=$((WARNINGS + 1))
}

# Check 1: Python version
echo "1. Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    REQUIRED_VERSION="3.11"
    if [[ "$PYTHON_VERSION" > "$REQUIRED_VERSION" ]] || [[ "$PYTHON_VERSION" == "$REQUIRED_VERSION" ]]; then
        print_status 0 "Python version $PYTHON_VERSION (>= $REQUIRED_VERSION required)"
    else
        print_status 1 "Python version $PYTHON_VERSION is too old (>= $REQUIRED_VERSION required)"
    fi
else
    print_status 1 "Python3 not found"
fi
echo ""

# Check 2: Required files exist
echo "2. Checking required files..."
REQUIRED_FILES=(
    "main.py"
    "requirements.txt"
    "Dockerfile"
    "railway.json"
    ".env.example"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_status 0 "Found $file"
    else
        print_status 1 "Missing $file"
    fi
done
echo ""

# Check 3: Environment variables
echo "3. Checking environment variables..."
REQUIRED_ENV_VARS=(
    "NOTION_API_KEY"
    "NOTION_DB_SYSTEM_INBOX"
    "NOTION_DB_EXECUTIVE_INTENTS"
    "NOTION_DB_ACTION_PIPES"
    "NOTION_DB_AGENT_REGISTRY"
    "NOTION_DB_EXECUTION_LOG"
    "NOTION_DB_TRAINING_DATA"
    "ANTHROPIC_API_KEY"
    "ANTHROPIC_MODEL"
)

if [ -f ".env" ]; then
    source .env
    for var in "${REQUIRED_ENV_VARS[@]}"; do
        if [ -n "${!var}" ]; then
            # Check if it's not a placeholder value
            if [[ "${!var}" == *"xxxx"* ]] || [[ "${!var}" == *"your"* ]]; then
                print_warning "$var is set but appears to be a placeholder"
            else
                print_status 0 "$var is set"
            fi
        else
            print_status 1 "$var is not set"
        fi
    done
else
    print_status 1 ".env file not found"
fi
echo ""

# Check 4: Dependencies
echo "4. Checking dependencies..."
if [ -f "requirements.txt" ]; then
    print_status 0 "requirements.txt found"

    # Check if venv exists
    if [ -d "venv" ]; then
        print_status 0 "Virtual environment found"
    else
        print_warning "Virtual environment not found (optional for Docker deployment)"
    fi
else
    print_status 1 "requirements.txt not found"
fi
echo ""

# Check 5: Docker
echo "5. Checking Docker..."
if command -v docker &> /dev/null; then
    print_status 0 "Docker is installed"

    # Try to build Docker image
    echo "   Building test Docker image..."
    if docker build -t executive-mind-matrix:test . > /dev/null 2>&1; then
        print_status 0 "Docker image builds successfully"
        docker rmi executive-mind-matrix:test > /dev/null 2>&1
    else
        print_status 1 "Docker image build failed"
    fi
else
    print_warning "Docker not found (not required for Railway deployment)"
fi
echo ""

# Check 6: Git repository
echo "6. Checking Git repository..."
if [ -d ".git" ]; then
    print_status 0 "Git repository found"

    # Check for uncommitted changes
    if [ -n "$(git status --porcelain)" ]; then
        print_warning "Uncommitted changes detected"
        git status --short
    else
        print_status 0 "No uncommitted changes"
    fi

    # Check current branch
    BRANCH=$(git branch --show-current)
    print_status 0 "Current branch: $BRANCH"
else
    print_warning "Not a git repository"
fi
echo ""

# Check 7: Security
echo "7. Security checks..."

# Check for secrets in code
if grep -r "sk-ant-" --include="*.py" --exclude-dir="venv" . > /dev/null 2>&1; then
    print_status 1 "Anthropic API key found in code (should be in .env only)"
else
    print_status 0 "No hardcoded Anthropic API keys detected"
fi

if grep -r "secret_" --include="*.py" --exclude-dir="venv" . > /dev/null 2>&1; then
    print_status 1 "Notion API key found in code (should be in .env only)"
else
    print_status 0 "No hardcoded Notion API keys detected"
fi

# Check .gitignore
if [ -f ".gitignore" ]; then
    if grep -q ".env" .gitignore; then
        print_status 0 ".env is in .gitignore"
    else
        print_status 1 ".env is NOT in .gitignore"
    fi
else
    print_status 1 ".gitignore not found"
fi
echo ""

# Check 8: Log directory
echo "8. Checking log directory..."
if [ -d "logs" ]; then
    print_status 0 "logs directory exists"
else
    mkdir -p logs
    print_status 0 "logs directory created"
fi
echo ""

# Check 9: Railway CLI (optional)
echo "9. Checking Railway CLI (optional)..."
if command -v railway &> /dev/null; then
    print_status 0 "Railway CLI is installed"

    # Check if logged in
    if railway whoami > /dev/null 2>&1; then
        print_status 0 "Logged into Railway"
    else
        print_warning "Not logged into Railway CLI"
    fi
else
    print_warning "Railway CLI not installed (can deploy via GitHub integration)"
fi
echo ""

# Summary
echo "================================"
echo "Summary"
echo "================================"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}⚠ $WARNINGS warning(s) found${NC}"
    fi
    echo ""
    echo "You are ready to deploy!"
    exit 0
else
    echo -e "${RED}✗ $ERRORS error(s) found${NC}"
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}⚠ $WARNINGS warning(s) found${NC}"
    fi
    echo ""
    echo "Please fix the errors before deploying."
    exit 1
fi

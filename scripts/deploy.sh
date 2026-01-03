#!/bin/bash

# QuantMind MCP Deployment Script
# This script automates the deployment of QuantMind MCP server

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENVIRONMENT="${1:-development}"
DOCKER_REGISTRY="${DOCKER_REGISTRY:-localhost}"
IMAGE_NAME="quantmind-mcp"
IMAGE_TAG="${2:-latest}"

# Functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."

    command -v docker >/dev/null 2>&1 || error "Docker is not installed"
    command -v docker-compose >/dev/null 2>&1 || error "Docker Compose is not installed"

    log "Prerequisites check passed"
}

# Setup environment
setup_environment() {
    log "Setting up environment for: $ENVIRONMENT"

    if [ ! -f "$PROJECT_ROOT/.env" ]; then
        if [ ! -f "$PROJECT_ROOT/.env.example" ]; then
            error "Neither .env nor .env.example found"
        fi

        log "Creating .env from .env.example"
        cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
        warning "Please update .env with your actual configuration values"
    fi

    # Update environment-specific variables
    case "$ENVIRONMENT" in
        production)
            log "Configuring for production environment"
            sed -i.bak 's/ENVIRONMENT=.*/ENVIRONMENT=production/' "$PROJECT_ROOT/.env"
            sed -i.bak 's/LOG_LEVEL=.*/LOG_LEVEL=WARNING/' "$PROJECT_ROOT/.env"
            ;;
        staging)
            log "Configuring for staging environment"
            sed -i.bak 's/ENVIRONMENT=.*/ENVIRONMENT=staging/' "$PROJECT_ROOT/.env"
            sed -i.bak 's/LOG_LEVEL=.*/LOG_LEVEL=INFO/' "$PROJECT_ROOT/.env"
            ;;
        development)
            log "Configuring for development environment"
            sed -i.bak 's/ENVIRONMENT=.*/ENVIRONMENT=development/' "$PROJECT_ROOT/.env"
            sed -i.bak 's/LOG_LEVEL=.*/LOG_LEVEL=DEBUG/' "$PROJECT_ROOT/.env"
            ;;
    esac

    # Cleanup backup files
    rm -f "$PROJECT_ROOT/.env.bak"
}

# Build Docker image
build_image() {
    log "Building Docker image: $IMAGE_NAME:$IMAGE_TAG"

    cd "$PROJECT_ROOT"
    docker build \
        -t "$IMAGE_NAME:$IMAGE_TAG" \
        -t "$IMAGE_NAME:latest" \
        -f Dockerfile \
        .

    if [ "$DOCKER_REGISTRY" != "localhost" ]; then
        log "Tagging image for registry: $DOCKER_REGISTRY"
        docker tag "$IMAGE_NAME:$IMAGE_TAG" "$DOCKER_REGISTRY/$IMAGE_NAME:$IMAGE_TAG"
        docker tag "$IMAGE_NAME:latest" "$DOCKER_REGISTRY/$IMAGE_NAME:latest"
    fi

    log "Docker image built successfully"
}

# Run tests
run_tests() {
    log "Running tests..."

    cd "$PROJECT_ROOT"

    if docker-compose run --rm quantmind-mcp python -m pytest tests/ -v; then
        log "Tests passed"
    else
        error "Tests failed"
    fi
}

# Start services
start_services() {
    log "Starting services..."

    cd "$PROJECT_ROOT"
    docker-compose up -d

    log "Waiting for services to be ready..."
    sleep 5

    # Check health
    if docker-compose ps | grep -q "healthy"; then
        log "Services started successfully"
    else
        warning "Services may not be healthy yet, waiting..."
        sleep 10
    fi
}

# Stop services
stop_services() {
    log "Stopping services..."

    cd "$PROJECT_ROOT"
    docker-compose down

    log "Services stopped"
}

# Show logs
show_logs() {
    log "Showing logs (Ctrl+C to exit)..."

    cd "$PROJECT_ROOT"
    docker-compose logs -f quantmind-mcp
}

# Validate deployment
validate_deployment() {
    log "Validating deployment..."

    # Check if container is running
    if ! docker-compose ps | grep -q "quantmind-mcp.*Up"; then
        error "Container is not running"
    fi

    # Check health endpoint (if exposed)
    if command -v curl >/dev/null 2>&1; then
        HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health || echo "000")
        if [ "$HEALTH_CHECK" = "200" ] || [ "$HEALTH_CHECK" = "404" ]; then
            log "Health check passed"
        else
            warning "Health check returned status: $HEALTH_CHECK"
        fi
    fi

    log "Deployment validation passed"
}

# Main deployment flow
deploy() {
    log "Starting deployment process..."
    log "Environment: $ENVIRONMENT"
    log "Image: $IMAGE_NAME:$IMAGE_TAG"

    check_prerequisites
    setup_environment
    build_image

    if [ "$ENVIRONMENT" != "development" ]; then
        run_tests
    fi

    start_services
    validate_deployment

    log "Deployment completed successfully!"
    log "Access the server at: http://localhost:8000"
}

# Parse arguments and run appropriate command
case "${ENVIRONMENT}" in
    deploy)
        ENVIRONMENT="development"
        deploy
        ;;
    stop)
        stop_services
        ;;
    logs)
        show_logs
        ;;
    restart)
        stop_services
        start_services
        ;;
    *)
        if [ -z "$ENVIRONMENT" ] || [ "$ENVIRONMENT" = "development" ] || [ "$ENVIRONMENT" = "staging" ] || [ "$ENVIRONMENT" = "production" ]; then
            deploy
        else
            echo "Usage: $0 [COMMAND] [ENVIRONMENT] [IMAGE_TAG]"
            echo ""
            echo "Commands:"
            echo "  deploy       Deploy the application (default)"
            echo "  stop         Stop the running services"
            echo "  logs         Show application logs"
            echo "  restart      Restart the services"
            echo ""
            echo "Environments:"
            echo "  development  Development environment (default)"
            echo "  staging      Staging environment"
            echo "  production   Production environment"
            echo ""
            echo "Image Tag:"
            echo "  latest       Use latest tag (default)"
            echo "  v1.0.0       Use specific version tag"
            echo ""
            echo "Examples:"
            echo "  $0 development latest"
            echo "  $0 production v1.0.0"
            exit 1
        fi
        ;;
esac

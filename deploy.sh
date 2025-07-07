#!/bin/bash

# Deployment script for Social Media Stats Dashboard
# Usage: ./deploy.sh [staging|production]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-staging}
APP_NAME="social-stats"
DEPLOY_PATH="/opt/${APP_NAME}-${ENVIRONMENT}"
BACKUP_PATH="/opt/backups/${APP_NAME}-${ENVIRONMENT}"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to backup current deployment
backup_current() {
    if [ -d "$DEPLOY_PATH" ]; then
        print_status "Creating backup of current deployment..."
        mkdir -p "$BACKUP_PATH"
        tar -czf "$BACKUP_PATH/backup-$(date +%Y%m%d-%H%M%S).tar.gz" -C "$DEPLOY_PATH" .
        print_status "Backup created successfully"
    fi
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command_exists docker; then
        print_error "Docker is not installed"
        exit 1
    fi
    
    if ! command_exists docker-compose; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    
    if ! command_exists git; then
        print_error "Git is not installed"
        exit 1
    fi
    
    print_status "All prerequisites are satisfied"
}

# Function to setup environment
setup_environment() {
    print_status "Setting up environment for $ENVIRONMENT..."
    
    # Create deployment directory
    mkdir -p "$DEPLOY_PATH"
    cd "$DEPLOY_PATH"
    
    # Clone or pull repository
    if [ -d ".git" ]; then
        print_status "Pulling latest changes..."
        git pull origin main
    else
        print_status "Cloning repository..."
        git clone https://github.com/your-username/social-media-stats-dashboard.git .
    fi
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_warning "Creating .env file from template..."
        cp .env.example .env
        print_warning "Please update .env file with your configuration"
        exit 1
    fi
    
    print_status "Environment setup completed"
}

# Function to build and deploy
deploy_application() {
    print_status "Building and deploying application..."
    
    cd "$DEPLOY_PATH"
    
    # Stop existing containers
    print_status "Stopping existing containers..."
    docker-compose down || true
    
    # Build new images
    print_status "Building Docker images..."
    docker-compose build --no-cache
    
    # Start services
    print_status "Starting services..."
    docker-compose up -d
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 30
    
    # Run database migrations
    print_status "Running database migrations..."
    docker-compose exec -T backend alembic upgrade head
    
    # Health check
    print_status "Performing health check..."
    if curl -f http://localhost/health >/dev/null 2>&1; then
        print_status "Health check passed"
    else
        print_error "Health check failed"
        docker-compose logs
        exit 1
    fi
    
    print_status "Deployment completed successfully"
}

# Function to rollback
rollback() {
    print_warning "Rolling back deployment..."
    
    cd "$DEPLOY_PATH"
    
    # Stop current containers
    docker-compose down
    
    # Find latest backup
    LATEST_BACKUP=$(ls -t "$BACKUP_PATH"/backup-*.tar.gz 2>/dev/null | head -1)
    
    if [ -n "$LATEST_BACKUP" ]; then
        print_status "Restoring from backup: $LATEST_BACKUP"
        tar -xzf "$LATEST_BACKUP" -C "$DEPLOY_PATH"
        docker-compose up -d
        print_status "Rollback completed"
    else
        print_error "No backup found for rollback"
        exit 1
    fi
}

# Function to show logs
show_logs() {
    print_status "Showing application logs..."
    cd "$DEPLOY_PATH"
    docker-compose logs -f
}

# Function to show status
show_status() {
    print_status "Showing application status..."
    cd "$DEPLOY_PATH"
    docker-compose ps
}

# Function to cleanup old backups
cleanup_backups() {
    print_status "Cleaning up old backups (keeping last 5)..."
    cd "$BACKUP_PATH"
    ls -t backup-*.tar.gz 2>/dev/null | tail -n +6 | xargs -r rm
}

# Main script logic
main() {
    case "$ENVIRONMENT" in
        staging|production)
            print_status "Starting deployment to $ENVIRONMENT environment"
            ;;
        *)
            print_error "Invalid environment. Use 'staging' or 'production'"
            exit 1
            ;;
    esac
    
    # Check if running as root
    if [ "$EUID" -eq 0 ]; then
        print_error "Please do not run this script as root"
        exit 1
    fi
    
    # Parse command line arguments
    case "${2:-deploy}" in
        deploy)
            check_prerequisites
            backup_current
            setup_environment
            deploy_application
            cleanup_backups
            ;;
        rollback)
            rollback
            ;;
        logs)
            show_logs
            ;;
        status)
            show_status
            ;;
        *)
            echo "Usage: $0 [staging|production] [deploy|rollback|logs|status]"
            echo "  deploy   - Deploy the application (default)"
            echo "  rollback - Rollback to previous version"
            echo "  logs     - Show application logs"
            echo "  status   - Show application status"
            exit 1
            ;;
    esac
}

# Run main function
main "$@" 
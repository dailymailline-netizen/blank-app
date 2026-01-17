#!/bin/bash
# Stream & Upload Hub - Deployment Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${GREEN}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            if [[ "$ID" == "ubuntu" ]]; then
                DISTRO="ubuntu"
            elif [[ "$ID" == "centos" ]] || [[ "$ID" == "rhel" ]]; then
                DISTRO="rhel"
            fi
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    else
        OS="unknown"
    fi
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 not found"
        exit 1
    fi
    print_success "Python $(python3 --version) found"
    
    # pip
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 not found"
        exit 1
    fi
    print_success "pip3 found"
    
    # Git (optional)
    if command -v git &> /dev/null; then
        print_success "Git found"
    else
        print_warning "Git not found (optional)"
    fi
}

# Setup Python environment
setup_environment() {
    print_header "Setting Up Python Environment"
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        print_warning "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate venv
    source venv/bin/activate || . venv/Scripts/activate
    print_success "Virtual environment activated"
    
    # Upgrade pip
    pip install --upgrade pip setuptools wheel
    print_success "pip upgraded"
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Dependencies installed"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Setup environment file
setup_env_file() {
    print_header "Setting Up Environment Configuration"
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_success ".env created from .env.example"
            print_warning "⚠️  Edit .env with your configuration"
        else
            print_error ".env.example not found"
            exit 1
        fi
    else
        print_success ".env already exists"
    fi
}

# Test storage backend
test_storage() {
    print_header "Testing Storage Backend"
    
    source .env || true
    
    if [ "$STORAGE_BACKEND" == "s3" ]; then
        if [ -z "$AWS_S3_BUCKET" ]; then
            print_error "AWS_S3_BUCKET not set in .env"
            return 1
        fi
        
        python3 << EOF
try:
    import boto3
    print("✅ boto3 is installed")
    # Test credentials by listing buckets
    s3 = boto3.client('s3', region_name='${AWS_REGION:-us-east-1}')
    buckets = s3.list_buckets()
    print(f"✅ AWS credentials valid, found {len(buckets['Buckets'])} bucket(s)")
except Exception as e:
    print(f"❌ AWS error: {e}")
    exit(1)
EOF
    else
        print_success "Using local storage backend"
    fi
}

# Create directories
create_directories() {
    print_header "Creating Required Directories"
    
    mkdir -p uploads
    mkdir -p streams
    mkdir -p community_notes
    mkdir -p logs
    mkdir -p temp
    
    print_success "Directories created"
}

# Run tests
run_tests() {
    print_header "Running Tests"
    
    if command -v pytest &> /dev/null; then
        if [ -d "tests" ]; then
            pytest tests/ -v
            print_success "Tests passed"
        else
            print_warning "No tests directory found"
        fi
    else
        print_warning "pytest not installed, skipping tests"
    fi
}

# Generate SSL certificates (self-signed)
generate_ssl_certs() {
    print_header "Generating SSL Certificates"
    
    mkdir -p ssl
    
    if [ ! -f "ssl/cert.pem" ] || [ ! -f "ssl/key.pem" ]; then
        openssl req -x509 -newkey rsa:4096 -nodes \
            -out ssl/cert.pem \
            -keyout ssl/key.pem \
            -days 365 \
            -subj "/C=US/ST=State/L=City/O=Org/CN=localhost"
        
        print_success "SSL certificates generated (self-signed)"
    else
        print_success "SSL certificates already exist"
    fi
}

# Deploy with Docker
deploy_docker() {
    print_header "Docker Deployment"
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker not installed"
        print_warning "Install Docker from https://docs.docker.com/get-docker/"
        return 1
    fi
    
    print_warning "Building Docker image..."
    docker build -t stream-hub:latest .
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "docker-compose not installed"
        return 1
    fi
    
    read -p "Deploy multi-instance setup with P2P? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        generate_ssl_certs
        docker-compose -f docker-compose-p2p.yml up -d
        print_success "Multi-instance deployment started"
        print_success "Access at:"
        echo "  - Instance 1: http://localhost:8501"
        echo "  - Instance 2: http://localhost:8502"
        echo "  - Instance 3: http://localhost:8503"
        echo "  - Load Balancer: http://localhost:80"
    fi
}

# Display final instructions
show_instructions() {
    print_header "Deployment Complete!"
    
    echo ""
    echo "Next steps:"
    echo ""
    echo "1. Review and configure .env:"
    echo "   nano .env"
    echo ""
    echo "2. Start the application:"
    echo ""
    
    source .env || true
    
    if [ "$STORAGE_BACKEND" == "s3" ]; then
        echo "   🔷 AWS S3 Backend (Production)"
        echo "   streamlit run streamlit_app.py"
    elif [ "$STORAGE_BACKEND" == "local" ]; then
        echo "   💾 Local Storage (Development)"
        echo "   streamlit run streamlit_app.py"
    fi
    
    echo ""
    echo "3. Access the application:"
    echo "   http://localhost:8501"
    echo ""
    echo "4. For multi-instance P2P setup:"
    echo "   See P2P_NFS_SETUP.md"
    echo "   docker-compose -f docker-compose-p2p.yml up -d"
    echo ""
    echo "Documentation:"
    echo "  - Quick Start: CLOUD_SETUP.md"
    echo "  - Architecture: CLOUD_ARCHITECTURE.md"
    echo "  - NFS Setup: P2P_NFS_SETUP.md"
    echo "  - Implementation: IMPLEMENTATION_SUMMARY.md"
    echo ""
}

# Main execution
main() {
    print_header "Stream & Upload Hub - Deployment Script"
    echo ""
    
    detect_os
    print_success "Detected OS: $OS"
    
    # Parse arguments
    MODE=${1:-"local"}
    
    case $MODE in
        "local")
            check_prerequisites
            setup_environment
            setup_env_file
            create_directories
            test_storage
            run_tests
            show_instructions
            ;;
        "docker")
            check_prerequisites
            setup_env_file
            generate_ssl_certs
            deploy_docker
            ;;
        "help")
            echo "Usage: ./deploy.sh [mode]"
            echo ""
            echo "Modes:"
            echo "  local    - Deploy locally with Python venv (default)"
            echo "  docker   - Deploy with Docker Compose"
            echo "  help     - Show this help message"
            echo ""
            ;;
        *)
            print_error "Unknown mode: $MODE"
            echo "Run './deploy.sh help' for usage"
            exit 1
            ;;
    esac
}

main "$@"

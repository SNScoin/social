# 🚀 Deployment Guide - Social Media Stats Dashboard

This guide will help you set up a complete CI/CD pipeline for your Social Media Stats Dashboard application.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [GitHub Actions CI/CD Setup](#github-actions-cicd-setup)
3. [Server Setup](#server-setup)
4. [Docker Deployment](#docker-deployment)
5. [Manual Deployment](#manual-deployment)
6. [Monitoring and Maintenance](#monitoring-and-maintenance)

---

## 🔧 Prerequisites

### Required Software
- **Git** - Version control
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **PostgreSQL** - Database (or use Docker)
- **Node.js** - For frontend builds
- **Python 3.11+** - Backend runtime

### Server Requirements
- **CPU**: 2+ cores
- **RAM**: 4GB+ (8GB recommended)
- **Storage**: 20GB+ SSD
- **OS**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+

---

## 🔄 GitHub Actions CI/CD Setup

### 1. Repository Configuration

1. **Fork/Clone** your repository to GitHub
2. **Enable GitHub Actions** in your repository settings
3. **Set up branch protection** for `main` and `develop` branches

### 2. GitHub Secrets Configuration

Go to your repository → Settings → Secrets and variables → Actions, and add:

#### Required Secrets:
```
STAGING_HOST=your-staging-server-ip
STAGING_USERNAME=deploy-user
STAGING_SSH_KEY=your-private-ssh-key

PRODUCTION_HOST=your-production-server-ip
PRODUCTION_USERNAME=deploy-user
PRODUCTION_SSH_KEY=your-private-ssh-key
```

#### Optional Secrets:
```
CODECOV_TOKEN=your-codecov-token
SENTRY_DSN=your-sentry-dsn
```

### 3. Branch Strategy

- **`main`** - Production deployments
- **`develop`** - Staging deployments
- **Feature branches** - Development work

### 4. Workflow Triggers

The CI/CD pipeline triggers on:
- **Push to `main`** → Deploy to production
- **Push to `develop`** → Deploy to staging
- **Pull requests** → Run tests only

---

## 🖥️ Server Setup

### 1. Initial Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y curl wget git unzip software-properties-common apt-transport-https ca-certificates gnupg lsb-release

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Node.js (for manual builds)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Python
sudo apt install -y python3 python3-pip python3-venv
```

### 2. Create Deployment User

```bash
# Create deployment user
sudo useradd -m -s /bin/bash deploy
sudo usermod -aG docker deploy

# Set up SSH key authentication
sudo mkdir -p /home/deploy/.ssh
sudo chmod 700 /home/deploy/.ssh
# Copy your public key to /home/deploy/.ssh/authorized_keys
sudo chown -R deploy:deploy /home/deploy/.ssh
```

### 3. Create Deployment Directories

```bash
# Create deployment directories
sudo mkdir -p /opt/social-stats-staging
sudo mkdir -p /opt/social-stats-production
sudo mkdir -p /opt/backups

# Set permissions
sudo chown -R deploy:deploy /opt/social-stats-*
sudo chown -R deploy:deploy /opt/backups
```

### 4. Environment Configuration

```bash
# Create environment files
sudo -u deploy cp env.example /opt/social-stats-staging/.env
sudo -u deploy cp env.example /opt/social-stats-production/.env

# Edit environment files with your configuration
sudo -u deploy nano /opt/social-stats-staging/.env
sudo -u deploy nano /opt/social-stats-production/.env
```

---

## 🐳 Docker Deployment

### 1. Quick Start with Docker Compose

```bash
# Clone repository
git clone https://github.com/your-username/social-media-stats-dashboard.git
cd social-media-stats-dashboard

# Copy environment file
cp env.example .env
# Edit .env with your configuration
nano .env

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 2. Production Deployment

```bash
# Build and start in production mode
docker-compose -f docker-compose.yml up -d --build

# Run database migrations
docker-compose exec backend alembic upgrade head

# Check health
curl http://localhost/health
```

### 3. Scaling and Load Balancing

For production, consider using:
- **Nginx** as reverse proxy
- **Traefik** for automatic SSL
- **Docker Swarm** or **Kubernetes** for orchestration

---

## 🛠️ Manual Deployment

### 1. Using the Deployment Script

```bash
# Make script executable
chmod +x deploy.sh

# Deploy to staging
./deploy.sh staging deploy

# Deploy to production
./deploy.sh production deploy

# Check status
./deploy.sh production status

# View logs
./deploy.sh production logs

# Rollback if needed
./deploy.sh production rollback
```

### 2. Manual Steps

```bash
# 1. Clone repository
git clone https://github.com/your-username/social-media-stats-dashboard.git
cd social-media-stats-dashboard

# 2. Set up environment
cp env.example .env
nano .env  # Configure your settings

# 3. Build frontend
cd frontend
npm install
npm run build
cd ..

# 4. Set up Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Set up database
# Create PostgreSQL database and user
sudo -u postgres createdb social_stats
sudo -u postgres createuser social_user

# 6. Run migrations
alembic upgrade head

# 7. Start application
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

---

## 📊 Monitoring and Maintenance

### 1. Health Monitoring

```bash
# Check application health
curl http://your-domain.com/health

# Monitor Docker containers
docker-compose ps
docker-compose logs -f

# Check system resources
htop
df -h
docker system df
```

### 2. Backup Strategy

```bash
# Database backup
docker-compose exec postgres pg_dump -U postgres social_stats > backup.sql

# Application backup
tar -czf app-backup-$(date +%Y%m%d).tar.gz /opt/social-stats-production

# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T postgres pg_dump -U postgres social_stats > /opt/backups/db_$DATE.sql
tar -czf /opt/backups/app_$DATE.tar.gz /opt/social-stats-production
find /opt/backups -name "*.sql" -mtime +7 -delete
find /opt/backups -name "*.tar.gz" -mtime +7 -delete
```

### 3. Log Management

```bash
# View application logs
tail -f logs/app.log

# View Docker logs
docker-compose logs -f backend

# Log rotation
sudo logrotate /etc/logrotate.d/social-stats
```

### 4. SSL Certificate Setup

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

---

## 🔒 Security Considerations

### 1. Firewall Configuration

```bash
# Configure UFW firewall
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 2. Environment Security

- Use strong, unique passwords
- Rotate API keys regularly
- Keep dependencies updated
- Use HTTPS in production
- Implement rate limiting

### 3. Database Security

```bash
# Secure PostgreSQL
sudo -u postgres psql
ALTER USER postgres PASSWORD 'strong-password';
CREATE USER app_user WITH PASSWORD 'app-password';
GRANT CONNECT ON DATABASE social_stats TO app_user;
```

---

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   # Check PostgreSQL status
   sudo systemctl status postgresql
   
   # Check connection
   psql -h localhost -U postgres -d social_stats
   ```

2. **Docker Build Fails**
   ```bash
   # Clean Docker cache
   docker system prune -a
   
   # Rebuild without cache
   docker-compose build --no-cache
   ```

3. **Application Won't Start**
   ```bash
   # Check logs
   docker-compose logs backend
   
   # Check environment variables
   docker-compose exec backend env
   ```

4. **Frontend Not Loading**
   ```bash
   # Check Nginx configuration
   docker-compose exec nginx nginx -t
   
   # Check frontend build
   ls -la frontend/build/
   ```

### Performance Optimization

1. **Database Optimization**
   ```sql
   -- Add indexes for better performance
   CREATE INDEX idx_links_company_id ON links(company_id);
   CREATE INDEX idx_metrics_link_id ON link_metrics(link_id);
   ```

2. **Caching Strategy**
   - Use Redis for session storage
   - Implement API response caching
   - Cache static assets

3. **Load Balancing**
   - Use multiple backend instances
   - Implement health checks
   - Use CDN for static assets

---

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review application logs
3. Check GitHub Issues
4. Contact the development team

---

## 🔄 Continuous Improvement

- Monitor application performance
- Update dependencies regularly
- Review and update security measures
- Optimize based on usage patterns
- Implement automated testing
- Set up monitoring and alerting 
# Deployment Guide

This guide covers different deployment options for the FX Payment Processor.

## Local Development

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Git

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd fx-payment-processor
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL**
   ```bash
   # Using Docker (recommended)
   docker run --name fx-postgres \
     -e POSTGRES_USER=fx_user \
     -e POSTGRES_PASSWORD=fx_password \
     -e POSTGRES_DB=fx_processor \
     -p 5432:5432 \
     -d postgres:15
   
   # Or install PostgreSQL locally and create database
   createdb fx_processor
   ```

5. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env file with your database credentials
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

The API will be available at `http://localhost:5000`

## Docker Development

### Quick Start
```bash
# Start both database and application
docker-compose up --build

# Run in background
docker-compose up -d --build

# View logs
docker-compose logs -f app

# Stop services
docker-compose down

# Clean up volumes
docker-compose down -v
```

### Individual Services
```bash
# Start only database
docker-compose up postgres

# Start only application (requires external DB)
docker-compose up app
```

## Production Deployment

### Docker Production Setup

1. **Create production docker-compose**
   ```yaml
   # docker-compose.prod.yml
   version: '3.8'
   
   services:
     postgres:
       image: postgres:15
       environment:
         POSTGRES_USER: ${DB_USER}
         POSTGRES_PASSWORD: ${DB_PASSWORD}
         POSTGRES_DB: ${DB_NAME}
       volumes:
         - postgres_data:/var/lib/postgresql/data
         - ./backups:/backups
       restart: unless-stopped
       healthcheck:
         test: ["CMD-SHELL", "pg_isready -U ${DB_USER} -d ${DB_NAME}"]
         interval: 10s
         timeout: 5s
         retries: 5
   
     app:
       build: .
       ports:
         - "5000:5000"
       environment:
         DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
         FLASK_ENV: production
         FLASK_DEBUG: "False"
       depends_on:
         postgres:
           condition: service_healthy
       restart: unless-stopped
       healthcheck:
         test: ["CMD", "curl", "-f", "http://localhost:5000/"]
         interval: 30s
         timeout: 10s
         retries: 3
   
   volumes:
     postgres_data:
   ```

2. **Create production environment file**
   ```bash
   # .env.prod
   DB_USER=fx_user_prod
   DB_PASSWORD=your_secure_password
   DB_NAME=fx_processor_prod
   ```

3. **Deploy**
   ```bash
   docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
   ```

### Cloud Deployment Options

#### AWS ECS/Fargate

1. **Build and push Docker image**
   ```bash
   # Build
   docker build -t fx-payment-processor .
   
   # Tag for ECR
   docker tag fx-payment-processor:latest \
     123456789012.dkr.ecr.us-east-1.amazonaws.com/fx-payment-processor:latest
   
   # Push to ECR
   docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/fx-payment-processor:latest
   ```

2. **Create ECS task definition**
3. **Set up RDS PostgreSQL instance**
4. **Configure ALB/NLB for load balancing**
5. **Deploy ECS service**

#### Google Cloud Run

1. **Build and deploy**
   ```bash
   gcloud run deploy fx-payment-processor \
     --source . \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars DATABASE_URL=postgresql://... \
     --memory 512Mi \
     --cpu 1
   ```

#### Azure Container Instances

1. **Build and push to ACR**
2. **Create Azure Database for PostgreSQL**
3. **Deploy container instance**

### Environment Variables

#### Required
- `DATABASE_URL`: PostgreSQL connection string
- `FLASK_ENV`: `development` or `production`

#### Optional
- `FLASK_DEBUG`: `True` or `False`
- `PORT`: Application port (default: 5000)

### Health Checks

The application provides health check endpoints:

- `GET /`: Basic API information and health
- Database connectivity is checked on startup

### Monitoring and Logging

#### Basic Monitoring
```bash
# Container health
docker-compose ps

# Application logs
docker-compose logs -f app

# Database logs
docker-compose logs -f postgres

# Resource usage
docker stats
```

#### Production Monitoring
- Use Prometheus + Grafana for metrics
- ELK/EFK stack for log aggregation
- APM tools like New Relic or DataDog

### Backup and Recovery

#### Database Backup
```bash
# Manual backup
docker-compose exec postgres pg_dump -U fx_user fx_processor > backup.sql

# Automated backup script
#!/bin/bash
DATE=$(date +"%Y%m%d_%H%M%S")
docker-compose exec postgres pg_dump -U fx_user fx_processor > "backup_$DATE.sql"
gzip "backup_$DATE.sql"
```

#### Database Restore
```bash
# Restore from backup
docker-compose exec -T postgres psql -U fx_user -d fx_processor < backup.sql
```

### SSL/TLS Configuration

For production, place the application behind a reverse proxy with SSL:

#### Nginx Configuration
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Performance Tuning

#### Database Optimization
- Connection pooling
- Proper indexing
- Regular VACUUM and ANALYZE

#### Application Optimization
- Use Gunicorn for production WSGI server
- Configure worker processes based on CPU cores
- Implement caching for FX rates

#### Example Gunicorn Configuration
```bash
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 app:app
```

### Security Considerations

1. **Database Security**
   - Use strong passwords
   - Restrict network access
   - Regular security updates

2. **Application Security**
   - Input validation (already implemented)
   - Rate limiting (implement as needed)
   - Authentication/Authorization (extend as needed)

3. **Infrastructure Security**
   - Network segmentation
   - Firewall rules
   - Regular security patches

### Scaling Considerations

#### Horizontal Scaling
- Multiple application instances behind load balancer
- Database connection pooling
- Stateless application design

#### Database Scaling
- Read replicas for reporting
- Connection pooling
- Database partitioning for large datasets

### Troubleshooting

#### Common Issues

1. **Database Connection Issues**
   ```bash
   # Check if database is running
   docker-compose ps postgres
   
   # Check database logs
   docker-compose logs postgres
   
   # Test connection
   docker-compose exec postgres psql -U fx_user -d fx_processor -c "SELECT 1;"
   ```

2. **Application Issues**
   ```bash
   # Check application logs
   docker-compose logs app
   
   # Check application health
   curl http://localhost:5000/
   
   # Check database connectivity from app
   docker-compose exec app python -c "from app import db; print('DB OK' if db else 'DB Error')"
   ```

3. **Memory/Performance Issues**
   ```bash
   # Monitor resource usage
   docker stats
   
   # Check application metrics
   # Implement /metrics endpoint with prometheus_client if needed
   ```
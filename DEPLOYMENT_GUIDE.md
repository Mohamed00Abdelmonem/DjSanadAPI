# Production Deployment Guide

## 🚀 Deploying to Production

This guide covers deploying the JWT authentication API to production on various platforms.

---

## 📋 Pre-Deployment Checklist

### Security
- [ ] Generate new `SECRET_KEY`
- [ ] Set `DEBUG = False`
- [ ] Set `SECURE_SSL_REDIRECT = True`
- [ ] Set `SESSION_COOKIE_SECURE = True`
- [ ] Set `CSRF_COOKIE_SECURE = True`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Configure `CORS_ALLOWED_ORIGINS`
- [ ] Run security check: `python manage.py check --deploy`

### Database
- [ ] Create new MongoDB database in production
- [ ] Use strong credentials (minimum 12 characters)
- [ ] Enable MongoDB IP whitelist
- [ ] Set up automated backups
- [ ] Test connection string

### Email
- [ ] Configure production email backend (SMTP)
- [ ] Generate Gmail app password (if using Gmail)
- [ ] Test email sending
- [ ] Verify sender email is properly configured

### Monitoring
- [ ] Set up logging to file/service
- [ ] Set up error tracking (Sentry)
- [ ] Configure uptime monitoring
- [ ] Set up database backups alerts

---

## 🐳 Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Run migrations and start server
CMD ["sh", "-c", "python manage.py migrate && gunicorn quickstart.wsgi:application --bind 0.0.0.0:8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      DEBUG: "False"
      SECRET_KEY: ${SECRET_KEY}
      MONGODB_URI: ${MONGODB_URI}
      EMAIL_BACKEND: ${EMAIL_BACKEND}
      EMAIL_HOST: ${EMAIL_HOST}
      EMAIL_PORT: ${EMAIL_PORT}
      EMAIL_USE_TLS: ${EMAIL_USE_TLS}
      EMAIL_HOST_USER: ${EMAIL_HOST_USER}
      EMAIL_HOST_PASSWORD: ${EMAIL_HOST_PASSWORD}
      FRONTEND_URL: ${FRONTEND_URL}
    depends_on:
      - db
    volumes:
      - ./logs:/app/logs

  db:
    image: mongo:6.0
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGO_USER}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_PASSWORD}
    volumes:
      - mongo_data:/data/db

volumes:
  mongo_data:
```

### Build and Run

```bash
# Build image
docker build -t sanad-api .

# Run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f web

# Stop services
docker-compose down
```

---

## ☁️ Heroku Deployment

### Procfile

```
web: gunicorn quickstart.wsgi:application --log-file -
worker: celery -A quickstart worker -l info
release: python manage.py migrate
```

### runtime.txt

```
python-3.11.7
```

### Deploy Steps

```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Add MongoDB addon
heroku addons:create mongolab:sandbox

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False
heroku config:set FRONTEND_URL=https://yourfrontend.com

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate

# View logs
heroku logs -t
```

---

## 🔷 AWS EC2 Deployment

### SSH into Instance

```bash
ssh -i your-key.pem ec2-user@your-instance-ip
```

### Install Dependencies

```bash
sudo yum update -y
sudo yum install python3 python3-pip git nginx supervisor -y

# Install Python dependencies
sudo pip3 install gunicorn django python-dotenv
pip3 install -r requirements.txt
```

### Configure Gunicorn

Create `/etc/supervisor/conf.d/sanad-api.conf`:

```ini
[program:sanad-api]
directory=/home/ec2-user/sanad-api
command=/usr/local/bin/gunicorn quickstart.wsgi:application --workers 3 --bind 127.0.0.1:8000
autostart=true
autorestart=true
stderr_logfile=/var/log/sanad-api/err.log
stdout_logfile=/var/log/sanad-api/out.log
```

### Configure Nginx

Create `/etc/nginx/conf.d/sanad-api.conf`:

```nginx
upstream sanad_api {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://sanad_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/ec2-user/sanad-api/static/;
    }
}
```

### Enable SSL with Let's Encrypt

```bash
sudo amazon-linux-extras install -y nginx1
sudo yum install certbot python3-certbot-nginx -y

sudo certbot --nginx -d yourdomain.com
```

### Start Services

```bash
sudo systemctl start supervisor
sudo systemctl start nginx
sudo systemctl enable supervisor
sudo systemctl enable nginx
```

---

## 🟢 DigitalOcean App Platform

### app.yaml

```yaml
name: sanad-api
services:
- name: api
  github:
    repo: username/sanad-api
    branch: main
  build_command: pip install -r requirements.txt && python manage.py migrate
  run_command: gunicorn quickstart.wsgi:application
  envs:
  - key: DEBUG
    value: "False"
    scope: RUN_AND_BUILD_TIME
  - key: SECRET_KEY
    value: ${SECRET_KEY}
    scope: RUN_AND_BUILD_TIME
  - key: MONGODB_URI
    value: ${MONGODB_URI}
    scope: RUN_AND_BUILD_TIME
  http_port: 8000
  instance_count: 1
  instance_size_slug: basic-xs
databases:
- name: mongodb
  engine: MONGODB
  version: "6.0"
  production: true
```

---

## 📊 Environment Variables for Production

Create `.env.production`:

```env
# Django
DEBUG=False
SECRET_KEY=generate-a-secure-key-with-50-chars
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Database
MONGODB_URI=mongodb+srv://production_user:strong_password@cluster.mongodb.net/sanad_prod?retryWrites=true

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# JWT
JWT_ACCESS_TOKEN_LIFETIME=15
JWT_REFRESH_TOKEN_LIFETIME=7

# Frontend
FRONTEND_URL=https://yourdomain.com
FRONTEND_RESET_PASSWORD_URL=https://yourdomain.com/reset-password
FRONTEND_ACTIVATE_ACCOUNT_URL=https://yourdomain.com/activate

# API
API_URL=https://yourdomain.com

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Logging
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project_id
```

### Generate Secure Secret Key

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

---

## 🔒 SSL/HTTPS Configuration

### Automatic with Let's Encrypt (Certbot)

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Generate certificate
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renew certificates
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### Manual with Existing Certificate

Update Nginx config:

```nginx
server {
    listen 443 ssl http2;
    ssl_certificate /etc/ssl/certs/yourdomain.com.crt;
    ssl_certificate_key /etc/ssl/private/yourdomain.com.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
}

server {
    listen 80;
    return 301 https://$host$request_uri;
}
```

---

## 📈 Performance Optimization

### Enable Caching

In `settings.py`:

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### Database Connection Pooling

```python
DATABASES = {
    'default': {
        'ENGINE': 'django_mongodb_backend',
        'NAME': 'sanad_db',
        'ENFORCE_SCHEMA_CHECKS': False,
        'CLIENT': {
            'maxPoolSize': 50,
            'minPoolSize': 10,
        }
    }
}
```

### Static Files

```bash
# Collect static files
python manage.py collectstatic --noinput

# Serve with Nginx or CDN
```

Configure Nginx:

```nginx
location /static/ {
    alias /var/www/sanad-api/static/;
    expires 365d;
    add_header Cache-Control "public, immutable";
}
```

---

## 🔍 Monitoring & Logging

### Sentry Integration

```bash
pip install sentry-sdk
```

In `settings.py`:

```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,
    send_default_pii=False,
)
```

### Logging to File

In `settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/sanad-api/sanad.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}
```

---

## 🔄 Backup Strategy

### MongoDB Backups

```bash
# Automated daily backup
0 2 * * * /usr/local/bin/mongodump --uri="mongodb+srv://user:pass@cluster.mongodb.net/sanad_prod" --out=/backups/mongodb/$(date +\%Y-\%m-\%d)

# Upload to S3
0 3 * * * /usr/local/bin/aws s3 sync /backups/mongodb s3://your-backup-bucket/mongodb/
```

---

## 📞 Maintenance

### Regular Tasks

- Weekly: Check logs for errors
- Weekly: Verify backups are working
- Monthly: Update dependencies (`pip install --upgrade -r requirements.txt`)
- Monthly: Review security updates
- Quarterly: Performance review
- Yearly: SSL certificate renewal check

### Database Maintenance

```bash
# Connect to MongoDB
mongosh "mongodb+srv://user:pass@cluster.mongodb.net/sanad_prod"

# Check indexes
db.users_user.getIndexes()

# Analyze query performance
db.users_user.find({email: "test@example.com"}).explain("executionStats")
```

---

## 🚨 Troubleshooting Production Issues

### 500 Error

1. Check logs: `tail -f /var/log/sanad-api/sanad.log`
2. Check Sentry for errors
3. Verify database connection
4. Check environment variables

### Slow Responses

1. Enable query logging
2. Check MongoDB indexes
3. Monitor CPU/memory usage
4. Consider caching or scaling

### Email Not Sending

1. Check email backend in settings
2. Verify SMTP credentials
3. Check spam folder
4. Review Django logs for errors

### SSL Issues

1. Verify certificate is not expired: `sudo certbot certificates`
2. Renew if needed: `sudo certbot renew --force-renewal`
3. Check Nginx config


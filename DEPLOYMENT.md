# SmartLearn Hub - Deployment Guide

## Prerequisites

- Docker 24+ and Docker Compose 2+
- Python 3.12+ (for local development)
- PostgreSQL 16+ (production)
- Redis 7+ (production)
- Domain name with DNS configured
- SSL certificates (Let's Encrypt recommended)
- Container registry (GHCR, Docker Hub, ECR, GCR)
- Kubernetes cluster (EKS, GKE, AKS) or cloud run service (Cloud Run, ECS Fargate)

---

## Quick Start (Local Development)

### 1. Clone and Configure

```bash
git clone https://github.com/your-org/smartlearn-hub.git
cd smartlearn-hub

# Copy environment template
cp .env.example .env

# Edit .env with your local settings
# At minimum set:
# - SECRET_KEY (generate with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
# - OPENAI_API_KEY (if using AI features)
```

### 2. Start Services

```bash
# Start all services (PostgreSQL, Redis, Django, Celery, Daphne)
docker-compose up -d

# View logs
docker-compose logs -f web

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

### 3. Access Application

- **Web App**: http://localhost:8000
- **Admin**: http://localhost:8000/admin
- **WebSocket**: ws://localhost:8001/ws/
- **Health Check**: http://localhost:8000/health/

---

## Production Deployment

### Option 1: Docker Compose (Single Server)

Best for: Small deployments, staging, simple hosting

#### 1. Prepare Server

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install -y docker.io docker-compose-plugin nginx certbot python3-certbot-nginx

# Add user to docker group
sudo usermod -aG docker $USER
# Log out and back in
```

#### 2. Configure Environment

```bash
# On server
mkdir -p /opt/smartlearn-hub
cd /opt/smartlearn-hub

# Copy docker-compose.prod.yml and .env.production
# Edit .env.production with production values:
# - Strong SECRET_KEY
# - Real DATABASE_URL (managed PostgreSQL recommended)
# - Real REDIS_URL (managed Redis recommended)
# - OPENAI_API_KEY
# - AWS credentials for S3 media storage
# - SENTRY_DSN for error tracking
# - EMAIL settings
# - ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
# - CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

#### 3. Set up SSL with Let's Encrypt

```bash
# Get initial certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Set up auto-renewal
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

#### 4. Configure Nginx

```bash
# Copy nginx.conf to /etc/nginx/nginx.conf
sudo cp nginx.conf /etc/nginx/nginx.conf

# Test and reload
sudo nginx -t
sudo systemctl reload nginx
```

#### 5. Deploy

```bash
# Pull and start
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput

# Collect static
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Verify health
curl -f https://yourdomain.com/health/
```

---

### Option 2: Kubernetes (Recommended for Production)

Best for: High availability, auto-scaling, production workloads

#### 1. Create Namespace and Secrets

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: smartlearn-hub
---
# k8s/secrets.yaml (apply with kubectl apply -f secrets.yaml)
apiVersion: v1
kind: Secret
metadata:
  name: smartlearn-secrets
  namespace: smartlearn-hub
type: Opaque
stringData:
  SECRET_KEY: "your-production-secret-key"
  DATABASE_URL: "postgresql://user:pass@host:5432/db"
  REDIS_URL: "redis://host:6379/0"
  OPENAI_API_KEY: "sk-..."
  SENTRY_DSN: "https://...@sentry.io/..."
  AWS_ACCESS_KEY_ID: "..."
  AWS_SECRET_ACCESS_KEY: "..."
  ALLOWED_HOSTS: "yourdomain.com,www.yourdomain.com"
  CSRF_TRUSTED_ORIGINS: "https://yourdomain.com,https://www.yourdomain.com"
```

#### 2. Deploy PostgreSQL (Use Managed Service in Production)

```yaml
# k8s/postgres.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: smartlearn-hub
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:16-alpine
        env:
        - name: POSTGRES_DB
          value: smartlearn_hub
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: smartlearn-secrets
              key: POSTGRES_USER
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: smartlearn-secrets
              key: POSTGRES_PASSWORD
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-data
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
  volumeClaimTemplates:
  - metadata:
      name: postgres-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 20Gi
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: smartlearn-hub
spec:
  ports:
  - port: 5432
  selector:
    app: postgres
```

#### 3. Deploy Redis (Use Managed Service in Production)

```yaml
# k8s/redis.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: smartlearn-hub
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        command: ["redis-server", "--appendonly", "yes", "--maxmemory", "512mb", "--maxmemory-policy", "allkeys-lru"]
        ports:
        - containerPort: 6379
        volumeMounts:
        - name: redis-data
          mountPath: /data
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
      volumes:
      - name: redis-data
        emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: smartlearn-hub
spec:
  ports:
  - port: 6379
  selector:
    app: redis
```

#### 4. Deploy Application

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: smartlearn-web
  namespace: smartlearn-hub
spec:
  replicas: 3
  selector:
    matchLabels:
      app: smartlearn-web
  template:
    metadata:
      labels:
        app: smartlearn-web
    spec:
      containers:
      - name: web
        image: ghcr.io/your-org/smartlearn-hub:latest
        ports:
        - containerPort: 8000
        envFrom:
        - secretRef:
            name: smartlearn-secrets
        env:
        - name: DJANGO_SETTINGS_MODULE
          value: "core.settings.production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: smartlearn-secrets
              key: DATABASE_URL
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: smartlearn-secrets
              key: REDIS_URL
        readinessProbe:
          httpGet:
            path: /health/
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /health/
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 30
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
---
# Celery Worker
apiVersion: apps/v1
kind: Deployment
metadata:
  name: smartlearn-celery
  namespace: smartlearn-hub
spec:
  replicas: 2
  selector:
    matchLabels:
      app: smartlearn-celery
  template:
    metadata:
      labels:
        app: smartlearn-celery
    spec:
      containers:
      - name: celery
        image: ghcr.io/your-org/smartlearn-hub:latest
        command: ["celery", "-A", "core", "worker", "-l", "info", "-Q", "default,ai_tasks,notifications,analytics", "--concurrency=4", "--prefetch-multiplier=1", "--max-tasks-per-child=1000"]
        envFrom:
        - secretRef:
            name: smartlearn-secrets
        env:
        - name: DJANGO_SETTINGS_MODULE
          value: "core.settings.production"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
---
# Celery Beat
apiVersion: apps/v1
kind: Deployment
metadata:
  name: smartlearn-celery-beat
  namespace: smartlearn-hub
spec:
  replicas: 1
  selector:
    matchLabels:
      app: smartlearn-celery-beat
  template:
    metadata:
      labels:
        app: smartlearn-celery-beat
    spec:
      containers:
      - name: celery-beat
        image: ghcr.io/your-org/smartlearn-hub:latest
        command: ["celery", "-A", "core", "beat", "-l", "info", "--scheduler", "django_celery_beat.schedulers:DatabaseScheduler"]
        envFrom:
        - secretRef:
            name: smartlearn-secrets
        env:
        - name: DJANGO_SETTINGS_MODULE
          value: "core.settings.production"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
# Daphne (WebSocket)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: smartlearn-daphne
  namespace: smartlearn-hub
spec:
  replicas: 2
  selector:
    matchLabels:
      app: smartlearn-daphne
  template:
    metadata:
      labels:
        app: smartlearn-daphne
    spec:
      containers:
      - name: daphne
        image: ghcr.io/your-org/smartlearn-hub:latest
        command: ["daphne", "-b", "0.0.0.0", "-p", "8001", "core.asgi:application"]
        ports:
        - containerPort: 8001
        envFrom:
        - secretRef:
            name: smartlearn-secrets
        env:
        - name: DJANGO_SETTINGS_MODULE
          value: "core.settings.production"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
```

#### 5. Services and Ingress

```yaml
# k8s/services.yaml
apiVersion: v1
kind: Service
metadata:
  name: smartlearn-web
  namespace: smartlearn-hub
spec:
  ports:
  - port: 8000
    targetPort: 8000
  selector:
    app: smartlearn-web
---
apiVersion: v1
kind: Service
metadata:
  name: smartlearn-daphne
  namespace: smartlearn-hub
spec:
  ports:
  - port: 8001
    targetPort: 8001
  selector:
    app: smartlearn-daphne
---
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: smartlearn-ingress
  namespace: smartlearn-hub
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1s"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "60"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "60"
    nginx.ingress.kubernetes.io/websocket-services: "smartlearn-daphne"
spec:
  tls:
  - hosts:
    - yourdomain.com
    - www.yourdomain.com
    secretName: smartlearn-tls
  rules:
  - host: yourdomain.com
    http:
      paths:
      - path: /ws
        pathType: Prefix
        backend:
          service:
            name: smartlearn-daphne
            port:
              number: 8001
      - path: /
        pathType: Prefix
        backend:
          service:
            name: smartlearn-web
            port:
              number: 8000
  - host: www.yourdomain.com
    http:
      paths:
      - path: /ws
        pathType: Prefix
        backend:
          service:
            name: smartlearn-daphne
            port:
              number: 8001
      - path: /
        pathType: Prefix
        backend:
          service:
            name: smartlearn-web
            port:
              number: 8000
```

#### 6. Apply Manifests

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Apply secrets (use kubectl create secret or sealed-secrets for GitOps)
kubectl apply -f k8s/secrets.yaml

# Deploy infrastructure
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/redis.yaml

# Wait for DB and Redis to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n smartlearn-hub --timeout=120s
kubectl wait --for=condition=ready pod -l app=redis -n smartlearn-hub --timeout=60s

# Run migrations (as a Job)
kubectl apply -f k8s/migration-job.yaml

# Deploy app
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/services.yaml
kubectl apply -f k8s/ingress.yaml

# Verify
kubectl get pods -n smartlearn-hub
kubectl logs -n smartlearn-hub -l app=smartlearn-web
```

---

### Option 3: Cloud Run / ECS Fargate / Azure Container Apps

Best for: Serverless containers, pay-per-use, minimal ops

#### Cloud Run (GCP)

```yaml
# cloudrun.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: smartlearn-hub
  annotations:
    run.googleapis.com/ingress: all
    run.googleapis.com/ingress-status: all
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "1"
        autoscaling.knative.dev/maxScale: "10"
        run.googleapis.com/cpu-throttling: "false"
        run.googleapis.com/memory: "1Gi"
        run.googleapis.com/cpu: "1000m"
    spec:
      containers:
      - image: gcr.io/PROJECT_ID/smartlearn-hub:latest
        ports:
        - containerPort: 8000
        env:
        - name: DJANGO_SETTINGS_MODULE
          value: "core.settings.production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: smartlearn-secrets
              key: DATABASE_URL
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: smartlearn-secrets
              key: REDIS_URL
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: smartlearn-secrets
              key: SECRET_KEY
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: smartlearn-secrets
              key: OPENAI_API_KEY
        readinessProbe:
          httpGet:
            path: /health/
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /health/
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 30
```

Deploy:
```bash
gcloud run services replace cloudrun.yaml --region=us-central1
```

---

## Database Migration Strategy

### Zero-Downtime Migrations

1. **Backward Compatible**: Add columns/tables, never remove in same deploy
2. **Separate Deploy**: Deploy code that works with old AND new schema
3. **Run Migration**: Apply migration
4. **Deploy Cleanup**: Remove old code paths

```bash
# Production migration command
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput

# Or in Kubernetes
kubectl exec -n smartlearn-hub deploy/smartlearn-web -- python manage.py migrate --noinput
```

### Rollback Procedure

```bash
# 1. Revert Docker image
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# 2. If migration was applied, create reverse migration
python manage.py migrate app_name previous_migration

# 3. Verify health
curl -f https://yourdomain.com/health/
```

---

## SSL/TLS Configuration

### Let's Encrypt with Certbot (Docker Compose)

```bash
# Initial cert
docker run -it --rm \
  -v "/etc/letsencrypt:/etc/letsencrypt" \
  -v "/var/lib/letsencrypt:/var/lib/letsencrypt" \
  -v "/var/www/certbot:/var/www/certbot" \
  certbot/certbot certonly \
  --webroot -w /var/www/certbot \
  -d yourdomain.com -d www.yourdomain.com

# Auto-renewal (add to crontab)
0 12 * * * docker run --rm -v "/etc/letsencrypt:/etc/letsencrypt" -v "/var/lib/letsencrypt:/var/lib/letsencrypt" -v "/var/www/certbot:/var/www/certbot" certbot/certbot renew --quiet && docker-compose -f /opt/smartlearn-hub/docker-compose.prod.yml exec nginx nginx -s reload
```

### Managed Certificates (AWS ACM, GCP Managed Certs, Azure App Gateway)

Use your cloud provider's managed certificate service with load balancer.

---

## Monitoring & Observability

### Health Checks

```bash
# Basic health
curl https://yourdomain.com/health/

# Detailed health (includes DB, Redis, Celery, OpenAI)
curl https://yourdomain.com/health/detail/
```

### Prometheus Metrics

```bash
# Metrics endpoint
curl https://yourdomain.com/metrics/

# Key metrics to alert on:
# - django_http_requests_total (rate > 0)
# - django_http_requests_latency_seconds (p99 < 1s)
# - django_db_queries_total (rate)
# - celery_tasks_total (success/failure rate)
# - websocket_connections_active
```

### Sentry Error Tracking

1. Create Sentry project
2. Add `SENTRY_DSN` to environment
3. Errors automatically captured

### Log Aggregation

```bash
# Docker Compose
docker-compose -f docker-compose.prod.yml logs -f --tail=100 web

# Kubernetes
kubectl logs -n smartlearn-hub -l app=smartlearn-web -f --tail=100
```

---

## Backup & Disaster Recovery

### Database Backup (Automated)

```bash
# Daily backup script (run via cron)
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker exec smartlearn-postgres-prod pg_dump -U smartlearn smartlearn_hub | gzip > /backups/smartlearn_${DATE}.sql.gz

# Keep last 30 days
find /backups -name "smartlearn_*.sql.gz" -mtime +30 -delete

# Upload to S3
aws s3 cp /backups/smartlearn_${DATE}.sql.gz s3://your-backup-bucket/postgres/
```

### Restore Procedure

```bash
# 1. Stop application
docker-compose -f docker-compose.prod.yml stop web celery daphne

# 2. Restore database
gunzip -c /backups/smartlearn_20240115_020000.sql.gz | docker exec -i smartlearn-postgres-prod psql -U smartlearn smartlearn_hub

# 3. Start application
docker-compose -f docker-compose.prod.yml start web celery daphne

# 4. Verify
curl -f https://yourdomain.com/health/
```

---

## Scaling Guidelines

### Horizontal Pod Autoscaler (Kubernetes)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: smartlearn-web-hpa
  namespace: smartlearn-hub
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: smartlearn-web
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
      - type: Pods
        value: 4
        periodSeconds: 15
      selectPolicy: Max
```

### Celery Scaling

```bash
# Scale workers based on queue depth
# Monitor: celery -A core inspect active_queues

# Add workers for specific queues
docker-compose -f docker-compose.prod.yml up -d --scale celery=4

# Or in Kubernetes
kubectl scale deployment smartlearn-celery --replicas=5 -n smartlearn-hub
```

---

## Security Checklist

- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` (50+ chars, random)
- [ ] `ALLOWED_HOSTS` restricted to your domains
- [ ] `SECURE_SSL_REDIRECT=True`
- [ ] `SESSION_COOKIE_SECURE=True`
- [ ] `CSRF_COOKIE_SECURE=True`
- [ ] `SECURE_HSTS_SECONDS=31536000`
- [ ] `SECURE_HSTS_INCLUDE_SUBDOMAINS=True`
- [ ] `SECURE_HSTS_PRELOAD=True`
- [ ] `SECURE_CONTENT_TYPE_NOSNIFF=True`
- [ ] `SECURE_BROWSER_XSS_FILTER=True`
- [ ] `X_FRAME_OPTIONS=DENY`
- [ ] CSP headers configured
- [ ] Rate limiting on auth endpoints
- [ ] Database credentials in secrets manager
- [ ] API keys in secrets manager
- [ ] Regular dependency updates (Dependabot)
- [ ] Security scanning in CI (bandit, safety)
- [ ] WAF enabled (Cloudflare, AWS WAF, etc.)

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| 502 Bad Gateway | Check if web container is running: `docker-compose ps` |
| Static files 404 | Run `collectstatic` and check nginx config |
| WebSocket connection failed | Check Daphne is running and nginx WebSocket config |
| Celery tasks not executing | Check Redis connection, worker logs |
| Database connection error | Verify DATABASE_URL, network connectivity |
| Migration fails | Check for data conflicts, run with `--fake` if needed |

### Debug Commands

```bash
# Check container health
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f web

# Shell into container
docker-compose -f docker-compose.prod.yml exec web bash

# Django shell
docker-compose -f docker-compose.prod.yml exec web python manage.py shell

# Check migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py showmigrations

# Test database connection
docker-compose -f docker-compose.prod.yml exec web python manage.py dbshell

# Test Redis
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping
```

---

## Maintenance Windows

### Weekly
- [ ] Review error rates in Sentry
- [ ] Check disk space on servers
- [ ] Review slow query logs
- [ ] Update dependencies (Dependabot PRs)

### Monthly
- [ ] Rotate secrets (DB password, API keys)
- [ ] Review and optimize database indexes
- [ ] Check backup integrity (test restore)
- [ ] Review monitoring alerts
- [ ] Update base Docker images

### Quarterly
- [ ] Security audit
- [ ] Load testing
- [ ] Disaster recovery drill
- [ ] Capacity planning review

---

## Rollback Checklist

1. [ ] Identify issue and confirm rollback needed
2. [ ] Revert to previous Docker image tag
3. [ ] Run reverse migrations if schema changed
4. [ ] Restart all services
5. [ ] Verify health checks pass
6. [ ] Monitor error rates for 15 minutes
7. [ ] Document incident and root cause
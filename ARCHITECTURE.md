# SmartLearn Hub - Architecture Overview

## System Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              EXTERNAL CLIENTS                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Web App   │  │ Mobile App  │  │   API       │  │   WebSocket         │ │
│  │  (HTMX)     │  │  (Future)   │  │  Clients    │  │  Clients (HTMX)     │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
└─────────┼────────────────┼────────────────┼─────────────────────┼────────────┘
          │                │                │                     │
          ▼                ▼                ▼                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            NGINX (Reverse Proxy)                            │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  SSL Termination  │  Rate Limiting  │  Gzip  │  Static Files  │ WS   │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          ▼                        ▼                        ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   Django App     │    │   Django App     │    │   Django App     │
│   (Gunicorn)     │    │   (Gunicorn)     │    │   (Daphne)       │
│   Workers: 4     │    │   Workers: 4     │    │   Workers: 2     │
│   Port: 8000     │    │   Port: 8000     │    │   Port: 8001     │
└────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SHARED INFRASTRUCTURE                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │  PostgreSQL  │  │    Redis     │  │   Celery     │  │   S3/Cloud     │  │
│  │  (Primary)   │  │  (Cluster)   │  │  Workers     │  │   Storage      │  │
│  │  Port: 5432  │  │  Port: 6379  │  │  (4 queues)  │  │  (Media files) │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Components

### Web Layer (Django + Gunicorn)
- **Framework**: Django 4.2 with Django REST Framework
- **WSGI Server**: Gunicorn with gthread workers (4 workers × 2 threads)
- **Static Files**: WhiteNoise + CDN (CloudFront/Cloudflare)
- **Security**: CSP, HSTS, CSRF, Rate limiting, Secure headers

### WebSocket Layer (Django Channels + Daphne)
- **ASGI Server**: Daphne (2 workers for WebSocket handling)
- **Channel Layer**: Redis-backed (separate DB)
- **Use Cases**: Real-time collaboration, notifications, live updates

### Background Processing (Celery + Redis)
- **Broker/Backend**: Redis (separate DBs for broker, results, cache)
- **Queues**: `default`, `ai_tasks`, `notifications`, `analytics`
- **Workers**: 4 concurrent workers with prefetch=1, max-tasks-per-child=1000
- **Beat**: Single beat scheduler with django-celery-beat

### Data Layer
- **Primary DB**: PostgreSQL 16 (managed: RDS/Cloud SQL/Neon)
- **Connection Pooling**: PgBouncer (transaction mode)
- **Caching**: Redis with django-redis (L2 cache)
- **Media Storage**: S3-compatible (AWS S3, GCS, Cloudflare R2)

### Observability
- **Error Tracking**: Sentry (Django + Celery + Channels)
- **Metrics**: Prometheus + Grafana (django-prometheus)
- **Logging**: Structured JSON logging (python-json-logger)
- **Tracing**: OpenTelemetry (planned)

## Data Flow

### HTTP Request Flow
1. Client → Nginx (SSL termination, rate limiting, static files)
2. Nginx → Gunicorn (load balanced across workers)
3. Django → Process request (middleware, views, serializers)
4. Django ↔ PostgreSQL (ORM queries, connection pooling)
5. Django ↔ Redis (cache, sessions, Celery tasks)
6. Response → Nginx → Client (compressed, cached headers)

### WebSocket Flow
1. Client → Nginx (WebSocket upgrade)
2. Nginx → Daphne (sticky sessions via Redis)
3. Daphne → Channels consumers (async)
4. Consumers ↔ Redis (channel layer, pub/sub)
5. Messages → Client via WebSocket

### Async Task Flow
1. Django view → Celery task (`.delay()` or `.apply_async()`)
2. Task → Redis broker (queue based on routing)
3. Celery worker → Executes task
4. Result → Redis backend
5. Optional: WebSocket notification to client

## Security Architecture

### Network Security
- All external traffic via HTTPS (TLS 1.2+)
- Internal services communicate via Docker network
- Database/Redis not exposed externally
- Nginx rate limiting on auth and API endpoints

### Application Security
- Django security middleware (CSRF, XSS, clickjacking)
- Content Security Policy (django-csp)
- Rate limiting (django-ratelimit)
- Secure cookies (HttpOnly, Secure, SameSite)
- SQL injection prevention (ORM parameterization)

### Secrets Management
- Environment variables for all secrets
- `.env.example` template in repo
- Production: AWS Secrets Manager / Doppler / 1Password
- Rotation: SECRET_KEY, OPENAI_API_KEY, DB passwords

## Deployment Architecture

### Development
```
┌─────────────────────────────────────────────────────────────────┐
│                      CI/CD Pipeline                              │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐             │
│  │  Lint   │→ │  Type   │→ │  Tests  │→ │ Security│             │
│  │ (black, │  │  Check  │  │ (pytest)│  │ (bandit,│             │
│  │  isort, │  │ (mypy)  │  │ +cov    │  │ safety) │             │
│  │ flake8) │  └────┬────┘  └────┬────┘  └────┬────┘             │
│  └────┬────┘       │           │           │                    │
│       │            ▼           ▼           ▼                    │
│       └────────── Build & Push Docker Image ───────────────────┘  │
│                    (GitHub Container Registry)                   │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
      ┌───────────────┐               ┌───────────────┐
      │   Staging     │               │  Production   │
      │  (Auto-deploy │               │  (Tag-based   │
      │   on main)    │               │   deploy)     │
      └───────┬───────┘               └───────┬───────┘
              │                               │
              ▼                               ▼
      ┌───────────────┐               ┌───────────────┐
      │ Docker Compose│               │ Kubernetes/ECS│
      │ (Single host) │               │ (Multi-AZ,    │
      │               │               │  Auto-scaling)│
      └───────────────┘               └───────────────┘
```

### Environments
| Environment | Purpose | Deploy Trigger | Infrastructure |
|-------------|---------|----------------|----------------|
| Development | Local dev | Manual | Docker Compose |
| Staging | Integration testing | Push to main | Docker Compose / K8s dev |
| Production | Live traffic | Git tag (v*) | K8s / ECS / Cloud Run |

## Scaling Strategy

### Horizontal Scaling
- **Web**: Add Gunicorn workers / replicas behind load balancer
- **WebSocket**: Add Daphne workers + Redis channel layer scaling
- **Celery**: Add workers per queue; priority queues for AI tasks
- **Database**: Read replicas for analytics; PgBouncer for connection pooling

### Vertical Scaling
- Increase container memory/CPU limits
- Database instance class upgrade
- Redis cluster mode for high throughput

### Caching Strategy
- **Template fragments**: Redis cache (5min TTL)
- **API responses**: Per-view caching (1-5min)
- **Sessions**: Redis-backed sessions
- **Static assets**: CDN with 1yr cache + immutable

## Disaster Recovery

### Backup Strategy
- **Database**: Daily snapshots + WAL archiving (RPO: 1hr, RTO: 30min)
- **Media**: S3 versioning + cross-region replication
- **Config**: GitOps (all infra as code)

### Recovery Procedures
1. Restore DB from latest snapshot
2. Replay WAL logs to target time
3. Deploy application from known-good image
4. Verify health checks pass
5. Switch DNS / load balancer

## Technology Stack Summary

| Layer | Technology | Version |
|-------|------------|---------|
| Language | Python | 3.12 |
| Web Framework | Django | 4.2 |
| API Framework | DRF | 3.14 |
| Real-time | Channels | 4.0 |
| Task Queue | Celery | 5.3 |
| Database | PostgreSQL | 16 |
| Cache/Queue | Redis | 7 |
| WSGI Server | Gunicorn | 21 |
| ASGI Server | Daphne | 4.0 |
| Reverse Proxy | Nginx | 1.25 |
| Container | Docker | 24 |
| Orchestration | K8s/ECS | Latest |
| CI/CD | GitHub Actions | - |
| Monitoring | Prometheus+Grafana | - |
| Error Tracking | Sentry | - |
| Logging | Loki/Grafana | - |
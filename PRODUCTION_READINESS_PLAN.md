# SmartLearn Hub - Production Readiness Plan

## Current State Assessment

| Area | Status | Gap |
|------|--------|-----|
| **Containerization** | ❌ None | No Dockerfile, docker-compose, .dockerignore |
| **CI/CD** | ❌ None | No GitHub Actions, GitLab CI, etc. |
| **Production Settings** | ⚠️ Partial | DEBUG=True in .env, SQLite, no security hardening |
| **Static/Media Files** | ⚠️ Dev only | No CDN, no WhiteNoise, no collectstatic in deploy |
| **Database** | ❌ SQLite | Needs PostgreSQL for production |
| **Secrets Management** | ❌ Plaintext .env | No vault/secrets manager integration |
| **Monitoring/Logging** | ❌ None | No Sentry, Datadog, structured logging |
| **Testing** | ⚠️ Empty stubs | No coverage, no CI test runs |
| **Security** | ⚠️ Basic | No CSP, HSTS, rate limiting, security headers |
| **Performance** | ❌ None | No caching, no DB connection pooling, no CDN |
| **Scalability** | ❌ None | Single process, no horizontal scaling config |
| **Backup/Recovery** | ❌ None | No DB backup strategy, no disaster recovery |
| **Documentation** | ⚠️ Minimal | No API docs, no deployment guide, no runbooks |

---

## Phase 1: Infrastructure & Deployment (Week 1-2)

### 1.1 Containerization
- [ ] Create `Dockerfile` (multi-stage: builder → runtime)
- [ ] Create `docker-compose.yml` (dev) + `docker-compose.prod.yml` (prod)
- [ ] Create `.dockerignore`
- [ ] Add `gunicorn` to requirements/prod.txt
- [ ] Configure non-root user in container
- [ ] Health check endpoint (`/health/`)

### 1.2 Production Settings
- [ ] Create `core/settings/production.py` extending base
- [ ] Create `core/settings/base.py` (shared config)
- [ ] Environment-specific settings via `DJANGO_SETTINGS_MODULE`
- [ ] Harden security settings:
  - `DEBUG=False`
  - `SECURE_SSL_REDIRECT=True`
  - `SECURE_HSTS_SECONDS=31536000`
  - `SECURE_CONTENT_TYPE_NOSNIFF=True`
  - `SECURE_BROWSER_XSS_FILTER=True`
  - `X_FRAME_OPTIONS='DENY'`
  - `SESSION_COOKIE_SECURE=True`
  - `CSRF_COOKIE_SECURE=True`
  - `CSRF_TRUSTED_ORIGINS` configured
  - `ALLOWED_HOSTS` from env

### 1.3 Database Migration
- [ ] Add `psycopg2-binary` to requirements/prod.txt
- [ ] Configure PostgreSQL in production settings
- [ ] Add connection pooling (`CONN_MAX_AGE=60`)
- [ ] Create migration scripts for production deployment

### 1.4 Static & Media Files
- [ ] Add `whitenoise` to requirements/prod.txt
- [ ] Configure `STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'`
- [ ] Configure media storage (S3/GCS) via `django-storages`
- [ ] Add `collectstatic` to Dockerfile/build step
- [ ] Configure CDN (CloudFront/Cloudflare) for static assets

### 1.5 Reverse Proxy & SSL
- [ ] Create `nginx.conf` for production
- [ ] Configure SSL/TLS (Let's Encrypt or managed certs)
- [ ] Rate limiting on auth endpoints
- [ ] Gzip compression
- [ ] Proxy headers for WebSocket (Channels) support

---

## Phase 2: CI/CD Pipeline (Week 2-3)

### 2.1 GitHub Actions / GitLab CI
- [ ] `.github/workflows/ci.yml`:
  - Lint (black, flake8, isort)
  - Type check (mypy if configured)
  - Test (pytest-django with coverage)
  - Security scan (bandit, safety)
  - Build Docker image
  - Push to registry on tag
- [ ] `.github/workflows/cd.yml`:
  - Deploy to staging on merge to main
  - Manual approval for production
  - Run migrations
  - Health check after deploy
  - Rollback on failure

### 2.2 Pre-commit Hooks
- [ ] `.pre-commit-config.yaml` with black, isort, flake8, bandit

### 2.3 Dependency Management
- [ ] Split requirements: `base.txt`, `dev.txt`, `prod.txt`
- [ ] Pin all dependencies with hashes (`pip-tools` or `pip-compile`)
- [ ] Dependabot/Renovate config for automated updates

---

## Phase 3: Security Hardening (Week 3)

### 3.1 Secrets Management
- [ ] Remove `.env` from repo (add to `.gitignore`)
- [ ] Create `.env.example` template
- [ ] Integrate with secrets manager (AWS Secrets Manager, GCP Secret Manager, HashiCorp Vault, or Doppler)
- [ ] Rotate `SECRET_KEY` and `OPENAI_API_KEY`

### 3.2 Application Security
- [ ] Add `django-csp` for Content Security Policy
- [ ] Add `django-ratelimit` or `django-axes` for auth endpoints
- [ ] Configure `django-secure` / security middleware
- [ ] Audit OpenAI API key usage (server-side only)
- [ ] Sanitize file uploads (notes, resources)
- [ ] Add CSRF protection for AJAX/HTMX endpoints

### 3.3 Dependency Security
- [ ] Run `safety check` / `pip-audit` in CI
- [ ] Pin transitive dependencies
- [ ] Regular vulnerability scanning

---

## Phase 4: Observability (Week 3-4)

### 4.1 Logging
- [ ] Structured JSON logging (`python-json-logger`)
- [ ] Configure log levels per environment
- [ ] Centralized logging (ELK, Datadog, CloudWatch, Loki)
- [ ] Request ID correlation middleware

### 4.2 Error Tracking
- [ ] Integrate Sentry (or GlitchTip self-hosted)
- [ ] Capture Django errors, Celery tasks, Channels consumers
- [ ] Configure release tracking

### 4.3 Metrics & Monitoring
- [ ] Prometheus metrics endpoint (`django-prometheus`)
- [ ] Key metrics: request latency, error rate, DB connections, Celery queue depth, WebSocket connections
- [ ] Grafana dashboards
- [ ] Uptime monitoring (UptimeRobot, Pingdom, or cloud provider)

### 4.4 Distributed Tracing
- [ ] OpenTelemetry integration for Django, Celery, Channels

---

## Phase 5: Performance & Scalability (Week 4)

### 5.1 Caching
- [ ] Redis cache backend for Django (`django-redis`)
- [ ] Cache templates, sessions, API responses
- [ ] Per-view caching for heavy endpoints
- [ ] Cache invalidation strategy

### 5.2 Database Optimization
- [ ] `select_related`/`prefetch_related` audit
- [ ] Add database indexes for common queries
- [ ] Connection pooling (PgBouncer)
- [ ] Read replicas for analytics queries

### 5.3 Background Workers
- [ ] Celery production config:
  - `worker_prefetch_multiplier=1`
  - `task_acks_late=True`
  - `worker_max_tasks_per_child=1000`
  - Priority queues
  - Monitoring (Flower)
- [ ] Separate queues for: default, ai_tasks, notifications, analytics

### 5.4 WebSocket Scaling (Channels)
- [ ] Redis channel layer (already configured)
- [ ] Multiple Daphne/Uvicorn workers
- [ ] Sticky sessions or Redis-backed session for WebSocket

### 5.5 CDN & Frontend Optimization
- [ ] Configure CloudFront/Cloudflare for static assets
- [ ] Enable Brotli compression
- [ ] Cache-Control headers for static files
- [ ] Consider HTMX partial caching

---

## Phase 6: Testing & Quality (Week 4-5)

### 6.1 Test Infrastructure
- [ ] `pytest-django` with `pytest-cov`
- [ ] Factory Boy for test data
- [ ] Test database (PostgreSQL in CI)
- [ ] Coverage threshold (min 80%)

### 6.2 Test Categories
- [ ] Unit tests for models, services, utils
- [ ] Integration tests for views, APIs
- [ ] WebSocket consumer tests
- [ ] Celery task tests
- [ ] E2E tests (Playwright/Cypress) for critical flows

### 6.3 Test in CI
- [ ] Run on every PR
- [ ] Coverage report upload (Codecov/Coveralls)
- [ ] Fail build on coverage drop

---

## Phase 7: Reliability & Operations (Week 5)

### 7.1 Health Checks
- [ ] `/health/` endpoint (DB, Redis, Celery, OpenAI)
- [ ] Kubernetes liveness/readiness probes
- [ ] Database migration health check

### 7.2 Backup & Disaster Recovery
- [ ] Automated PostgreSQL backups (daily + WAL archiving)
- [ ] Media file backup (S3 versioning or separate backup)
- [ ] Restore procedure documented and tested
- [ ] RPO/RTO defined

### 7.3 Deployment Safety
- [ ] Blue-green or rolling deployments
- [ ] Pre-deploy migration check
- [ ] Post-deploy smoke tests
- [ ] Automated rollback on health check failure

### 7.4 Runbooks
- [ ] Incident response runbook
- [ ] Common operations: deploy, rollback, scale, backup, restore
- [ ] On-call escalation

---

## Phase 8: Documentation & Developer Experience (Ongoing)

### 8.1 Technical Documentation
- [ ] `ARCHITECTURE.md` - system diagram, data flow
- [ ] `DEPLOYMENT.md` - step-by-step deploy guide
- [ ] `DEVELOPMENT.md` - local setup, debugging, common tasks
- [ ] `API.md` - DRF endpoints (auto-generate with drf-spectacular)
- [ ] `WEBSOCKET_API.md` - Channels events
- [ ] `CELERY_TASKS.md` - task definitions, schedules

### 8.2 API Documentation
- [ ] Add `drf-spectacular` for OpenAPI schema
- [ ] Swagger UI / Redoc at `/api/docs/`

### 8.3 Operational Docs
- [ ] Runbook for each service
- [ ] Alerting runbooks (what to do when X fires)
- [ ] Capacity planning guide

---

## Requirements Files Structure

```
requirements/
├── base.txt          # Shared: Django, DRF, Channels, Celery, OpenAI, etc.
├── dev.txt           # -r base.txt + black, flake8, isort, pytest, debug-toolbar
├── prod.txt          # -r base.txt + gunicorn, whitenoise, psycopg2, django-storages, sentry, prometheus
└── testing.txt       # -r base.txt + pytest-django, factory-boy, coverage
```

---

## Dockerfile (Multi-stage)

```dockerfile
# Builder stage
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements/ ./requirements/
RUN pip install --no-cache-dir -r requirements/prod.txt

# Runtime stage
FROM python:3.12-slim AS runtime
WORKDIR /app
RUN useradd -m -u 1000 appuser
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --chown=appuser:appuser . .
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 CMD curl -f http://localhost:8000/health/ || exit 1
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

---

## Priority Matrix

| Priority | Items | Effort |
|----------|-------|--------|
| **P0 - Blockers** | Docker, Prod settings, PostgreSQL, Secrets, CI/CD, Health checks | High |
| **P1 - Critical** | Static/media (S3), Security headers, Logging, Sentry, Backups, SSL | High |
| **P2 - Important** | Caching, Celery tuning, Monitoring dashboards, Rate limiting, Tests | Medium |
| **P3 - Nice to have** | CDN, OpenTelemetry, Blue-green deploy, E2E tests, API docs | Medium |
| **P4 - Polish** | Runbooks, Architecture docs, Capacity planning, Load testing | Low |

---

## Estimated Timeline

| Phase | Duration | Parallelizable |
|-------|----------|----------------|
| 1. Infrastructure & Deployment | 2 weeks | Partial |
| 2. CI/CD Pipeline | 1 week | After Phase 1 |
| 3. Security Hardening | 1 week | After Phase 1 |
| 4. Observability | 1-2 weeks | Parallel with 3 |
| 5. Performance & Scalability | 1-2 weeks | After Phase 1, 3 |
| 6. Testing & Quality | 1-2 weeks | Parallel with 4, 5 |
| 7. Reliability & Operations | 1 week | After Phase 1, 4 |
| 8. Documentation | Ongoing | Continuous |

**Total: ~6-8 weeks for full production readiness**

---

## Quick Wins (Do First - 1-2 days)

1. [ ] Create `requirements/prod.txt` with gunicorn, whitenoise, psycopg2, sentry-sdk
2. [ ] Create `core/settings/production.py` with security hardening
3. [ ] Add `.env.example` and remove `.env` from git
4. [ ] Create `Dockerfile` and `docker-compose.yml` for local dev
5. [ ] Add `/health/` endpoint
6. [ ] Configure GitHub Actions for lint + test
7. [ ] Enable `SECURE_SSL_REDIRECT` and HSTS in production settings

---

## Notes for This Project

### Special Considerations
- **WebSockets (Channels)**: Need Daphne/Uvicorn + Nginx WebSocket proxy config
- **Celery + Redis**: Separate Redis DBs for broker, cache, channel layer
- **OpenAI API**: Server-side only; implement rate limiting and cost monitoring
- **HTMX**: Partial renders need CSRF handling; consider `django-htmx` CSRF exempt for trusted origins
- **Custom User Model**: Already in `accounts.User` - ensure migrations are production-safe
- **SQLite → PostgreSQL**: Data migration needed if existing data matters

### Recommended Tech Stack Additions
| Need | Recommendation |
|------|----------------|
| Container Orchestration | Docker Compose (dev), Kubernetes/EKS/GKE/ECS (prod) |
| Registry | GitHub Container Registry (ghcr.io) |
| Secrets | 1Password CLI, Doppler, or cloud provider secrets manager |
| Monitoring | Sentry (errors) + Prometheus/Grafana (metrics) |
| Logging | Loki + Grafana or Datadog/CloudWatch |
| CI/CD | GitHub Actions (simple) or GitLab CI |
| Database | Managed PostgreSQL (RDS, Cloud SQL, Neon) |
| Redis | Managed (ElastiCache, Redis Cloud, Upstash) |
| Media Storage | S3 (AWS) / GCS / Cloudflare R2 |
| CDN | CloudFront / Cloudflare |

---

## Next Steps

1. **Review this plan** - confirm priorities, adjust timeline
2. **Pick Phase 1 tasks** - start with Docker + production settings
3. **Set up CI/CD** - enables safe iteration on all other phases
4. **Iterate in small PRs** - each phase broken into reviewable chunks

Would you like me to start implementing any specific phase? I recommend starting with **Phase 1 (Docker + Production Settings)** and **Phase 2 (CI/CD)** in parallel.
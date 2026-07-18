# SmartLearn Hub - Agent Guide

## Project Overview
Django 4.2 project with multiple apps: accounts, courses, analytics, ai_assistant, notes, collaboration.
Uses DRF, Channels (WebSockets), Celery + Redis, OpenAI, HTMX, Crispy Forms + Tailwind.

## Key Commands

```bash
# Install deps (dev includes black, flake8, isort)
pip install -r requirements/dev.txt

# Run migrations
python manage.py migrate

# Run dev server
python manage.py runserver

# Run tests (standard Django test runner)
python manage.py test

# Run specific app tests
python manage.py test apps.accounts

# Lint/format (dev deps required)
black .
flake8 .
isort .
```

## Environment
- Uses `.env` in `core/` for config (SECRET_KEY, DEBUG, OPENAI_API_KEY, etc.)
- SQLite by default (`db.sqlite3`)
- Redis required for Celery/Channels (localhost:6379)
- Custom user model: `accounts.User` (set in `AUTH_USER_MODEL`)

## Project Structure
```
apps/
  accounts/     # Custom user model, auth
  courses/      # Course management
  analytics/    # Analytics/dashboard
  ai_assistant/ # OpenAI integration
  notes/        # Note-taking
  collaboration/# Real-time collab (Channels)
core/           # Django settings, URLs, ASGI/WSGI
templates/      # Base templates (Tailwind + HTMX)
static/         # Static assets
```

## Key Conventions
- Apps registered in `INSTALLED_APPS` with `AppConfig` classes
- URLs namespaced per app (e.g., `analytics:dashboard`)
- HTMX middleware enabled for partial renders
- Crispy Forms configured for Tailwind
- Celery configured with Redis broker/result backend

## Testing
- Standard Django `TestCase` in each app's `tests.py`
- Currently empty test stubs - no test runner config needed beyond `python manage.py test`

## Dev Notes
- `.env` in `core/` loads via `python-dotenv` in settings
- `sys.path` modified in settings to include `apps/` directory
- Run `python manage.py collectstatic` for production static files
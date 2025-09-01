# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  PIP_NO_CACHE_DIR=1 \
  POETRY_VERSION=1.8.3 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_NO_INTERACTION=1 \
  PATH="/root/.local/bin:$PATH" \
  PYTHONPATH=/app

# System deps (libpq for Postgres, curl for health checks)
RUN apt-get update \
  && apt-get install -y --no-install-recommends build-essential libpq-dev curl ca-certificates netcat-openbsd \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Poetry and project deps (only prod/main group)
RUN pip install --upgrade pip "poetry==$POETRY_VERSION"
COPY pyproject.toml ./
# If lock file present copy for better caching
COPY poetry.lock ./
RUN poetry install --only main --no-root || poetry install --only main --no-root

## Copy project source (after deps for layer cache)
COPY manage.py ./
COPY quiz_project ./quiz_project
COPY accounts ./accounts
COPY quizzes ./quizzes
COPY submissions ./submissions
COPY realtime ./realtime
COPY core ./core
COPY api ./api
COPY templates ./templates
COPY assets ./assets
COPY static ./static

# Create staticfiles dir (collectstatic will populate at runtime)
RUN mkdir -p /app/staticfiles

EXPOSE 8000

ENV DJANGO_SETTINGS_MODULE=quiz_project.settings DJANGO_DEBUG=0

# Entry script handles migrations, collectstatic, then runs Daphne (ASGI)
COPY <<'EOF' /entrypoint.sh
#!/usr/bin/env bash
set -euo pipefail

if [ "${WAIT_FOR_HOST:-}" ] && [ "${WAIT_FOR_PORT:-}" ]; then
  echo "Waiting for $WAIT_FOR_HOST:$WAIT_FOR_PORT ..."
  for i in {1..60}; do
    if nc -z "$WAIT_FOR_HOST" "$WAIT_FOR_PORT" 2>/dev/null; then
      echo "Service available."; break
    fi
    sleep 1
  done
fi

python manage.py migrate --noinput
python manage.py collectstatic --noinput --clear

exec daphne -b 0.0.0.0 -p 8000 quiz_project.asgi:application
EOF
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

# Quizzy

A Django-based quiz platform with web UI, a REST API, and realtime leaderboards.

## Features
- Create quizzes with questions and answers (admin UI)
- Public or private (invite-only) quizzes
  - Accept or decline invitations via UI
- Attempt submission and scoring (best/first/last strategies)
- REST API for quizzes and submissions
- Realtime leaderboard updates via WebSockets (Channels)

## Tech stack
- Django 5, Django REST Framework
- Django Channels (ASGI); in-memory channel layer by default
- SQLite for local development
- Bootstrap 5 (custom SCSS build) + jQuery enhancements

## Quick start (local dev)

Prerequisites:
- Python 3.11+ (tested with 3.12)
- Bash shell

1) Clone and enter the project
```bash
git clone <your-fork-or-repo-url> quizzy
cd quizzy
```

2) Create and activate a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate
```

3) Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4) Initialize the database
```bash
python manage.py migrate --noinput
python manage.py createsuperuser  # follow prompts
```

5) Run the development server
```bash
python manage.py runserver
```

Visit:
- Home: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/
- Login: http://127.0.0.1:8000/accounts/login/

## Using the app
- Create quizzes, questions, and answers in the Django admin.
- Mark a quiz as published to make it visible in the list/detail pages.
- For private quizzes, invite users by email from the quiz detail page (creator only). The invited user accepts and can take the quiz.

## REST API
Base path: `/api/`

- List public quizzes
  - GET `/api/quizzes/`
- Quiz detail (enforces visibility/invite rules)
  - GET `/api/quizzes/{id}/`
- Submit answers (session-authenticated)
  - POST `/api/quizzes/{id}/submit`
  - Body (JSON):
    ```json
    { "answers": { "<question_id>": <answer_id> } }
    ```
- Invite a user (creator only)
  - POST `/api/quizzes/{id}/invite` with `{ "email": "user@example.com" }`
- Accept invite (invited user)
  - POST `/api/quizzes/{id}/accept`
- Decline invite (invited user)
  - POST `/api/quizzes/{id}/decline`
- Your submissions (session-authenticated)
  - GET `/api/submissions/`

Authentication:
- The API uses Django session auth in dev. Login at `/accounts/login/` in your browser before using write endpoints from the same browser session (or use a tool that can handle CSRF/session cookies).

## Realtime leaderboard
- WebSocket URL: `ws://127.0.0.1:8000/ws/quizzes/{quiz_id}/leaderboard/`
- The quiz detail page opens a WebSocket and logs leaderboard updates in the browser console.
- Channel layer: in-memory by default (works locally without Redis).

Optional (Redis channel layer):
- If you prefer Redis for Channels and caching in dev:
  - Run Redis locally and update `quiz_project/settings.py` `CHANNEL_LAYERS` to use `channels_redis.core.RedisChannelLayer` with your Redis URL.

## Running tests
Run all tests (verbose):
```bash
python manage.py test -v 2
```
If you run into unittest discovery conflicts in unconventional environments, you can target app test packages explicitly:
```bash
python manage.py test api.tests accounts.tests quizzes.tests submissions.tests core.tests -v 2
```

## Project layout (high level)
```
quiz_project/           # Django project (settings, urls, asgi, routing)
accounts/               # Auth backend (email or username), tests
quizzes/                # Domain models, web views, templates, invites
submissions/            # Submissions, attempts, scoring strategies, signals
api/                    # DRF serializers, viewsets, permissions, urls
realtime/               # Channels consumers and leaderboard utils
core/                   # Middleware and common helpers
templates/              # Base templates
static/                 # Static assets (lightweight in dev)
requirements.txt        # Python dependencies
```

## Frontend build (Bootstrap SCSS)

Install Node dependencies and build CSS once:
```bash
npm install
npm run build
```

For live rebuild during development:
```bash
npm run dev
```

Inputs/outputs:
- Source: `assets/scss/theme.scss` (imports `_variables.scss` + Bootstrap)
- Output: `static/css/app.css` (referenced in `templates/base.html`)

JavaScript enhancements:
- jQuery (auto-dismiss alerts, dynamic answer formset, future leaderboard flashes) loaded via `static/js/enhancements.js`.

## Troubleshooting
- WebSocket not connecting: ensure you’re using the `ws://` URL on localhost and the dev server is running. Reverse proxies may require extra ASGI/WebSocket config.
- CSRF errors on API POST: use session auth from a logged-in browser session or include CSRF headers appropriately.

## Next steps
- For production, configure Postgres and Redis, switch the channel layer/cache backend, collectstatic, and consider enabling ManifestStaticFilesStorage for cache busting.

## S3-Compatible Storage (Media & Static)

All file and (optionally) static asset storage can use any S3-compatible backend via `django-storages`.

### Environment Variables
Set the following (examples shown for MinIO dev):

```
USE_S3=1
AWS_STORAGE_BUCKET_NAME=quizzy-dev
AWS_ACCESS_KEY_ID=minio
AWS_SECRET_ACCESS_KEY=minio123456
AWS_S3_ENDPOINT_URL=http://127.0.0.1:9000        # MinIO / custom endpoint
AWS_S3_REGION_NAME=us-east-1                     # or your region
AWS_QUERYSTRING_AUTH=0                           # unsigned URLs for public-read
USE_SEPARATE_STATIC_BUCKET=1                     # optional: separate static bucket
STATIC_AWS_STORAGE_BUCKET_NAME=quizzy-dev-static # if separating
```

Optional overrides:
```
AWS_S3_SIGNATURE_VERSION=s3v4
AWS_DEFAULT_ACL=public-read
STATIC_AWS_DEFAULT_ACL=public-read
MEDIA_AWS_DEFAULT_ACL=private
```

### Running MinIO Locally

You can use the included `docker-compose.dev.yaml` which already starts MinIO, or run manually:

```bash
docker run -p 9000:9000 -p 9001:9001 \
  -e MINIO_ROOT_USER=minio \
  -e MINIO_ROOT_PASSWORD=minio123456 \
  -v $(pwd)/.minio-data:/data \
  quay.io/minio/minio:RELEASE.2024-06-29T01-20-47Z server /data --console-address ":9001"
```

Create the buckets (one time):
```bash
mc alias set local http://127.0.0.1:9000 minio minio123456
mc mb local/quizzy-dev
mc mb local/quizzy-dev-static
mc policy set public local/quizzy-dev-static   # if you want public-read static assets
```

### Collecting Static Files to S3

If `USE_SEPARATE_STATIC_BUCKET=1` is set, run:
```bash
python manage.py collectstatic --noinput
```
Static files will upload to the `static/` prefix inside the static bucket.

### Switching to AWS S3 (Production)
Change only environment variables (no code changes needed):
```
AWS_STORAGE_BUCKET_NAME=your-prod-bucket
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...secret...
AWS_S3_REGION_NAME=us-east-1
AWS_S3_ENDPOINT_URL=   # leave empty for AWS
AWS_QUERYSTRING_AUTH=1 # if you want signed URLs for private content
USE_SEPARATE_STATIC_BUCKET=1
STATIC_AWS_STORAGE_BUCKET_NAME=your-prod-static-bucket
```

Then deploy and run `collectstatic` in your release step.

### Public vs Private Media
If you need private user uploads, keep `AWS_QUERYSTRING_AUTH=1` (signed URLs). For entirely public assets (like quiz images) you can set an ACL of `public-read` and disable signing with `AWS_QUERYSTRING_AUTH=0`.

#### Public / Private Buckets & Per-User Isolation
You can optionally separate:

```
PUBLIC_MEDIA_AWS_STORAGE_BUCKET_NAME=quizzy-public
PRIVATE_MEDIA_AWS_STORAGE_BUCKET_NAME=quizzy-private
PUBLIC_MEDIA_LOCATION=public
PRIVATE_MEDIA_LOCATION=private
```

Per-user path isolation helper (example model):
```python
from django.db import models
from quiz_project.storage import PrivateUserMediaStorage, user_prefixed_path

class Profile(models.Model):
  user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
  avatar = models.ImageField(
    storage=PrivateUserMediaStorage(),
    upload_to=user_prefixed_path('avatars'),
    blank=True,
  )
```
This stores files like: `private/users/<user_id>/avatars/<uuid>.jpg`

### Fallback (Local Storage)
Set `USE_S3=0` to revert to Django's default local filesystem storage (useful for quick experiments without MinIO running).


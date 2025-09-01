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

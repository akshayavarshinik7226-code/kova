# KOVA

KOVA is a student-facing project deployment platform in development. The current release is a Flask application with SQLite authentication and a responsive Stage 1 UI foundation. Real project upload and deployment are not yet connected.

## Requirements

- Python 3.10+
- Dependencies from `requirements.txt`

## Local setup

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Windows PowerShell: Copy-Item .env.example .env
python manage.py create-admin --email admin@example.com --name "KOVA Admin"
python run.py
```

Open http://127.0.0.1:5000. The CLI prompts for a 12+ character password. Do not put real secrets in source control.

## Tests

```bash
python -m unittest discover -s tests -t . -v
python -m compileall -q .
```

## Current status

See `PROJECT_STATUS.md`, `IMPLEMENTATION_CHECKLIST.md`, `docs/ARCHITECTURE.md` and `TESTING_REPORT.md`. Demo dashboard content is illustrative. No real file upload or deployment is performed by the current UI.

# PythonAnywhere Deployment Guide

## Project Overview

- Django project entry point: `quickstart.wsgi:application`
- Main settings file: `quickstart/settings.py`
- Management command entry point: `manage.py`
- MongoDB backend: `django-mongodb-backend` with `MONGODB_URI`
- Static file handling: Django staticfiles + WhiteNoise

## Compatibility Notes

- Django `5.2.13` is compatible with Python 3.10+.
- `django-mongodb-backend` `5.2.3` and `pymongo` `4.17.0` are present in `requirements.txt` and are suitable for a MongoDB Atlas-backed deployment.
- PythonAnywhere support depends on the Python version you select for the web app. Use a Python 3.10+ environment.
- The app will fail to boot if `SECRET_KEY` or `MONGODB_URI` is missing.

## Exact Deployment Steps

1. Create a new PythonAnywhere web app.
2. Select a Python 3.10+ version that matches your virtual environment plan.
3. Set the working directory to the project root:
   `D:\Projects-Django\sanadApi\venv\quickstart`
4. Create or select a virtual environment for the app.
5. Install dependencies inside that environment:
   `pip install -r requirements.txt`
6. Set the WSGI entry point to:
   `quickstart.wsgi:application`
7. Configure environment variables in a `.env` file for local use, and set the same values in PythonAnywhere where appropriate.
8. Run static collection:
   `python manage.py collectstatic --noinput`
9. Reload the web app from the PythonAnywhere Web tab.

## Required Environment Variables

Set these in PythonAnywhere or through a secure environment management process:

- `SECRET_KEY`
- `DEBUG=False`
- `MONGODB_URI`

Recommended:

- `ALLOWED_HOSTS=<yourusername>.pythonanywhere.com`
- `PYTHONANYWHERE_HOST=<yourusername>.pythonanywhere.com`
- `FRONTEND_URL` if the API is called from a separate frontend origin
- `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL` if email features are used

## WSGI File Notes

PythonAnywhere typically provides a WSGI file in the Web tab. Make sure it:

- Points to the correct project directory
- Uses the active virtual environment
- Imports the Django app as `quickstart.wsgi:application`

Example pattern:

```python
import os
import sys

path = '/home/yourusername/quickstart'
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quickstart.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## Static Files Mapping

- URL: `/static/`
- Directory: `/home/yourusername/quickstart/staticfiles/`

If you change `STATIC_ROOT`, update the PythonAnywhere static file mapping to match.

## Required Commands

From the project directory:

```bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py check
```

## Reload Procedure

After changing code or settings:

1. Save the file changes.
2. Re-run `collectstatic` if static files changed.
3. Go to the PythonAnywhere Web tab.
4. Click Reload.
5. Check the error log if the site does not start.

## Common Troubleshooting

- `ModuleNotFoundError`: the virtual environment is not selected or dependencies were not installed.
- `SECRET_KEY environment variable must be set`: the web app is missing required environment variables.
- `MONGODB_URI environment variable must be set`: Atlas connection string was not configured.
- `DisallowedHost`: add the PythonAnywhere domain to `ALLOWED_HOSTS`.
- Static files 404s: verify the PythonAnywhere static mapping and rerun `collectstatic`.
- MongoDB connection failures: confirm Atlas network access allows the PythonAnywhere outbound IP or your chosen allowlist rule.

## Blockers to Check Before Going Live

- MongoDB Atlas IP allowlist must permit connections from PythonAnywhere.
- The PythonAnywhere environment must use Python 3.10 or newer.
- `requirements.txt` must be installed into the same virtual environment referenced by the WSGI app.
- `collectstatic` must succeed before reload.

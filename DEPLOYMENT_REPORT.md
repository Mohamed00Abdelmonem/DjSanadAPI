# Render Deployment Report

## Changes Made

- Updated [quickstart/settings.py](quickstart/settings.py) to read `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, and `MONGODB_URI` from environment variables.
- Added optional `.env` loading from the project root for local development only.
- Replaced the hardcoded MongoDB Atlas URI with environment-driven configuration while keeping `django-mongodb-backend` intact.
- Added WhiteNoise static-file support with `STATIC_ROOT`, `STORAGES`, and `WhiteNoiseMiddleware`.
- Added [build.sh](build.sh) for Render build preparation.

## Render Environment Variables

Required:

- `SECRET_KEY`
- `DEBUG=False`
- `MONGODB_URI`

Recommended:

- `ALLOWED_HOSTS=your-service.onrender.com`
- `RENDER_EXTERNAL_HOSTNAME` is optional, but supported if Render provides it
- `FRONTEND_URL` if the API is called from a browser app on another origin
- `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, and `DEFAULT_FROM_EMAIL` if email features are used in production

## Render Build Command

Use:

`bash build.sh`

## Render Start Command

Use:

`gunicorn quickstart.wsgi:application`

## MongoDB Atlas Notes

- Create a MongoDB Atlas database user with the correct password and permissions.
- Store the Atlas connection string in `MONGODB_URI`.
- Allow Render to reach the cluster by adding an appropriate Network Access rule in Atlas. If fixed outbound IPs are not available, allow `0.0.0.0/0` only if that matches your security policy.
- Keep the database name and query parameters in the URI consistent with the cluster you want to use.

## Verification

- `gunicorn` is present in [requirements.txt](requirements.txt).
- `whitenoise` is present in [requirements.txt](requirements.txt).
- `Django` is present in [requirements.txt](requirements.txt).
- `django-mongodb-backend` is present in [requirements.txt](requirements.txt).

## Warnings

- The application will fail to start if `SECRET_KEY` or `MONGODB_URI` is missing.
- `collectstatic` now runs during build, so any static collection issues will fail the deployment early.
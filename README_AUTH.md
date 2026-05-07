# Sanad - Production-Ready JWT Authentication API

## 🎯 Overview

**Sanad** is a complete, production-ready authentication system built with Django, Django REST Framework, and JWT tokens. It's designed for high-security applications and includes email verification, password reset, token management, and comprehensive API documentation.

### ✨ Key Features

- 🔐 **JWT Authentication** - Secure, stateless authentication with access and refresh tokens
- 📧 **Email Verification** - Secure email verification with token-based activation
- 🔑 **Password Management** - Secure password reset, change password, and recovery
- 🗄️ **MongoDB Ready** - Full MongoDB support with ObjectIdAutoField
- 📱 **REST API** - Complete RESTful API with proper HTTP status codes
- 📚 **API Documentation** - Auto-generated Swagger/OpenAPI docs and ReDoc
- 🛡️ **Security** - CORS, CSRF protection, password validation, token expiration
- 👤 **Custom User Model** - Email-based authentication (no username)
- 💼 **Production Ready** - Scalable, deployable to cloud platforms

---

## 📚 Documentation

### Quick Links
- **[Authentication Documentation](AUTHENTICATION_DOCS.md)** - Complete API reference
- **[API Examples](API_EXAMPLES.md)** - cURL examples and common use cases
- **[Frontend Integration](FRONTEND_INTEGRATION.md)** - How to use from React, Vue, etc.
- **[Deployment Guide](DEPLOYMENT_GUIDE.md)** - Deploy to Heroku, AWS, DigitalOcean, Docker

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example file
cp .env.example .env

# Edit .env with your configuration:
# - DATABASE_URL (MongoDB connection string)
# - EMAIL configuration (Gmail, SendGrid, etc.)
# - JWT_SECRET (generate with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
# - FRONTEND_URL (e.g., http://localhost:3000)
```

### 3. Run Migrations

```bash
python manage.py migrate
```

### 4. Start Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000/api/docs/` for interactive API documentation.

---

## 📡 API Endpoints

All endpoints are under `/api/auth/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/register/` | Create new user account |
| POST | `/activate/` | Verify email & activate account |
| POST | `/login/` | Login with email/password |
| POST | `/google/` | Login with Google ID token |
| POST | `/token/refresh/` | Get new access token |
| GET | `/me/` | Get authenticated user info |
| POST | `/change-password/` | Change password (authenticated) |
| POST | `/forgot-password/` | Request password reset |
| POST | `/reset-password/` | Reset password with token |

### Quick Example: Register

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "name": "John Doe",
    "password": "SecurePassword123!",
    "password_confirm": "SecurePassword123!"
  }'
```

### Quick Example: Login

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }'

# Response:
# {
#   "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
#   "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
#   "user_id": "507f1f77bcf86cd799439011",
#   "email": "user@example.com",
#   "name": "John Doe"
# }
```

### Quick Example: Google Login

```bash
curl -X POST http://localhost:8000/api/auth/google/ \
   -H "Content-Type: application/json" \
   -d '{
      "id_token": "GOOGLE_ID_TOKEN"
   }'
```

### Quick Example: Authenticated Request

```bash
curl -X GET http://localhost:8000/api/auth/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🔑 User Model

```python
class User(AbstractBaseUser, PermissionsMixin):
    id = ObjectIdAutoField(primary_key=True)  # MongoDB ObjectId
    email = EmailField(unique=True)           # Login identifier
    name = CharField(max_length=255)          # User's full name
    
    is_active = BooleanField(default=False)   # Must verify email first
    is_staff = BooleanField(default=False)    # Admin privileges
    is_superuser = BooleanField(default=False) # Superuser privileges
    
    email_verified_at = DateTimeField(null=True)
    password_changed_at = DateTimeField()
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'  # Login uses email, not username
```

---

## 🔐 Complete Authentication Flow

```
1. USER REGISTRATION
   POST /api/auth/register/
   ├─ Input: email, name, password
   ├─ Validation: email unique, password strong
   ├─ User created with is_active=False
   ├─ Verification email sent (with 24-hour token)
   └─ Response: User created, check email

2. EMAIL VERIFICATION
   POST /api/auth/activate/
   ├─ Input: token (from email link)
   ├─ Token validation: must be valid and not expired
   ├─ User: is_active=True, email_verified_at=now()
   └─ Response: Email verified, ready to login

3. USER LOGIN
   POST /api/auth/login/
   ├─ Input: email, password
   ├─ Validation: email exists, password correct, is_active=True
   ├─ Tokens generated:
   │  ├─ Access token (15 minutes valid)
   │  └─ Refresh token (7 days valid)
   └─ Response: Both tokens + user data

4. AUTHENTICATED REQUESTS
   GET /api/auth/me/
   ├─ Headers: Authorization: Bearer {access_token}
   ├─ Token validation: must be valid and not expired
   └─ Response: User data

5. TOKEN REFRESH
   POST /api/auth/token/refresh/
   ├─ Input: refresh_token (from login)
   ├─ Validation: refresh token valid and not expired
   ├─ New access token generated
   └─ Response: New access token

6. PASSWORD RESET FLOW
   a) Request reset: POST /api/auth/forgot-password/
      ├─ Input: email
      ├─ If user exists: send reset email (1-hour token)
      └─ Response: Always 200 (no user enumeration)
   
   b) Reset password: POST /api/auth/reset-password/
      ├─ Input: token, new_password, confirm_password
      ├─ Token validation: must be valid and not expired
      ├─ Passwords match: required
      ├─ Password updated, tokens cleared
      └─ Response: Password reset successful

7. CHANGE PASSWORD (Authenticated)
   POST /api/auth/change-password/
   ├─ Headers: Authorization: Bearer {access_token}
   ├─ Input: old_password, new_password, confirm_password
   ├─ Validation: old password correct, new != old
   └─ Response: Password changed
```

---

## 📧 Email Configuration

### Development (Console Backend - Default)
Emails print to console. Perfect for testing without SMTP server.

```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### Production (Gmail)

1. Enable 2-factor authentication on your Google account
2. Generate app password: https://myaccount.google.com/apppasswords
3. Update `.env`:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

### Production (SendGrid)

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.your_sendgrid_api_key
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

### Production (AWS SES)

```env
EMAIL_BACKEND=django_ses.SESBackend
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_SES_REGION_NAME=us-east-1
AWS_SES_REGION_ENDPOINT=email.us-east-1.amazonaws.com
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

---

## 🛡️ Security Features

- ✅ **Password Hashing**: PBKDF2 with 600,000 iterations (Django default)
- ✅ **Password Validation**: Minimum 8 characters, complexity checks
- ✅ **JWT Signing**: HMAC-SHA256 with unique per-environment key
- ✅ **Token Expiration**: 
  - Access tokens: 15 minutes
  - Refresh tokens: 7 days
  - Email verification: 24 hours
  - Password reset: 1 hour
- ✅ **Email Verification**: Users must verify email before login (is_active gate)
- ✅ **CORS Protection**: Only allow requests from configured frontend
- ✅ **CSRF Protection**: Django middleware enabled
- ✅ **User Enumeration Prevention**: Forgot password endpoint returns 200 always
- ✅ **SQL Injection Protection**: MongoDB with parameterized queries
- ✅ **Rate Limiting**: DRF throttling available for sensitive endpoints
- ✅ **Password History**: password_changed_at field for audit trail
- ✅ **Last Login Tracking**: last_login field from AbstractBaseUser

---

## 📊 Project Structure

```
sanad-api/
├── authentication/              # JWT auth app
│   ├── models.py               # (empty - uses User from users app)
│   ├── views.py                # 7 API endpoint views
│   ├── serializers.py          # Request/response validators
│   ├── utils.py                # Token & email utilities
│   ├── urls.py                 # /api/auth/* routing
│   ├── apps.py                 # App configuration
│   └── templates/
│       └── authentication/
│           └── emails/
│               ├── verify_email.html    # Verification email template
│               └── reset_password.html  # Password reset template
│
├── users/                      # Custom User model app
│   ├── models.py               # User(AbstractBaseUser, PermissionsMixin)
│   ├── admin.py                # Django admin customization
│   ├── managers.py             # CustomUserManager
│   ├── apps.py                 # App configuration
│   └── migrations/
│       ├── 0001_initial.py
│       ├── 0002_alter_user_id.py
│       └── 0003_alter_user_options_... .py
│
├── quickstart/                 # Project settings
│   ├── settings.py             # Django + JWT + CORS + Email config
│   ├── urls.py                 # Main URL routing + Swagger
│   ├── wsgi.py                 # WSGI application
│   └── asgi.py                 # ASGI application
│
├── other_apps/                 # Existing apps
│   ├── profiles/
│   ├── assessment_runs/
│   ├── recommendation_runs/
│   ├── chat_sessions/
│   └── chat_messages/
│
├── .env                        # Environment variables (git ignored)
├── .env.example                # Example .env (git tracked)
├── requirements.txt            # Python dependencies
├── manage.py                   # Django CLI
├── README.md                   # This file
├── AUTHENTICATION_DOCS.md      # Detailed auth documentation
├── API_EXAMPLES.md             # API usage examples
├── FRONTEND_INTEGRATION.md     # Frontend integration guide
└── DEPLOYMENT_GUIDE.md         # Deployment instructions
```

---

## 🧪 Testing the Authentication System

### Option 1: Interactive Swagger UI
```
1. Start server: python manage.py runserver
2. Visit: http://localhost:8000/api/docs/
3. Click on each endpoint to test
```

### Option 2: cURL Commands
See [API_EXAMPLES.md](API_EXAMPLES.md) for complete examples

### Option 3: Postman
1. Import schema: `http://localhost:8000/api/schema/`
2. Create environment variable: `access_token`
3. Test endpoints one by one

### Option 4: Python Script
```python
import requests

BASE_URL = "http://localhost:8000/api/auth"

# 1. Register
response = requests.post(f"{BASE_URL}/register/", json={
    "email": "test@example.com",
    "name": "Test User",
    "password": "TestPassword123!",
    "password_confirm": "TestPassword123!"
})
print(response.json())

# 2. Activate (get token from console output)
response = requests.post(f"{BASE_URL}/activate/", json={
    "token": "your-token-here"
})
print(response.json())

# 3. Login
response = requests.post(f"{BASE_URL}/login/", json={
    "email": "test@example.com",
    "password": "TestPassword123!"
})
tokens = response.json()
print(tokens)

# 4. Get user info
headers = {"Authorization": f"Bearer {tokens['access']}"}
response = requests.get(f"{BASE_URL}/me/", headers=headers)
print(response.json())
```

---

## 📦 Installed Dependencies

```
Django==5.2.13
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.0
django-cors-headers==4.3.0
django-mongodb-backend==5.2.3
drf-spectacular==0.27.0
python-dotenv==1.0.0
PyJWT==2.8.0
pymongo==4.6.0
PyYAML==6.0.1
```

See `requirements.txt` for complete list with versions.

---

## 🚀 Deployment

### Heroku
```bash
git push heroku main
heroku run python manage.py migrate
heroku config:set SECRET_KEY=your-secret-key
heroku config:set EMAIL_HOST_PASSWORD=your-password
```

### AWS EC2
See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

### Docker
```bash
docker build -t sanad .
docker run -p 8000:8000 sanad
```

### DigitalOcean
See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

---

## 🔒 Production Security Checklist

Before deploying:

- [ ] Generate new `SECRET_KEY` (don't use development key)
- [ ] Set `DEBUG = False` in settings.py
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Set `SECURE_SSL_REDIRECT = True`
- [ ] Configure HTTPS certificate
- [ ] Update `CORS_ALLOWED_ORIGINS` with your frontend domain
- [ ] Set strong database password
- [ ] Configure email backend with real SMTP credentials
- [ ] Run `python manage.py check --deploy`
- [ ] Set up monitoring/logging (Sentry, CloudWatch, etc.)
- [ ] Enable database backups
- [ ] Configure rate limiting on sensitive endpoints
- [ ] Set up CI/CD pipeline
- [ ] Enable HSTS, CSP headers
- [ ] Use environment-specific settings

---

## 🐛 Troubleshooting

### Issue: "No module named 'rest_framework_simplejwt'"
```bash
pip install -r requirements.txt
pip list | grep simplejwt
```

### Issue: CORS errors when calling from frontend
Check `CORS_ALLOWED_ORIGINS` in settings.py:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://yourdomain.com",
]
```

### Issue: Email not being sent
1. Check `EMAIL_BACKEND` is set correctly in .env
2. For Gmail: use app password, not regular password
3. Check Django logs for SMTP errors
4. Verify SMTP credentials in .env
5. Test with console backend first

### Issue: Invalid token error
- Token may have expired (access tokens: 15 min, refresh tokens: 7 days)
- Try logging in again
- Check token hasn't been modified
- Verify `JWT_SIGNING_KEY` is correct

### Issue: Email verification link not working
- Check token parameter in URL
- Verify token hasn't expired (24-hour limit)
- Check email backend is configured
- Make sure `FRONTEND_URL` in settings matches your frontend

See [AUTHENTICATION_DOCS.md](AUTHENTICATION_DOCS.md) for more troubleshooting.

---

## 📞 Support & Resources

- [Detailed Authentication Documentation](AUTHENTICATION_DOCS.md) - Complete API reference
- [API Examples](API_EXAMPLES.md) - cURL, Postman, Python examples
- [Frontend Integration](FRONTEND_INTEGRATION.md) - React, Vue, Angular examples
- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Production deployment
- [Django REST Framework Docs](https://www.django-rest-framework.org/)
- [djangorestframework-simplejwt](https://django-rest-framework-simplejwt.readthedocs.io/)
- [JWT.io](https://jwt.io/) - JWT specification
- [Django Security Docs](https://docs.djangoproject.com/en/5.2/topics/security/)

---

## 📝 License

This project is provided as-is for production and educational use.

---

## ✅ Checklist for Getting Started

1. ✅ Install dependencies: `pip install -r requirements.txt`
2. ✅ Configure `.env` file with your settings
3. ✅ Run migrations: `python manage.py migrate`
4. ✅ Start server: `python manage.py runserver`
5. ✅ Visit Swagger docs: `http://localhost:8000/api/docs/`
6. ✅ Test register endpoint: POST /api/auth/register/
7. ✅ Check console/email for verification link
8. ✅ Verify email with token
9. ✅ Login and get JWT tokens
10. ✅ Make authenticated requests with access token

---

**Ready to build something amazing? Let's go! 🚀**

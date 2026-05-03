# JWT Authentication System - Complete Documentation

## 🚀 Overview

This is a **production-ready JWT authentication system** built with Django, Django REST Framework, and djangorestframework-simplejwt. It includes:

- ✅ Custom User Model (email-based, no username)
- ✅ User Registration with Email Verification
- ✅ JWT Login/Logout
- ✅ Token Refresh
- ✅ Password Reset with Secure Tokens
- ✅ Change Password (Authenticated)
- ✅ Password Strength Validation
- ✅ CORS Support
- ✅ Swagger/OpenAPI Documentation
- ✅ MongoDB Support
- ✅ Rate Limiting Ready

---

## 📦 Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Key Packages:**
- `Django==5.2.13` - Web framework
- `djangorestframework==3.14.0` - API framework
- `djangorestframework-simplejwt==5.3.2` - JWT tokens
- `drf-spectacular==0.27.0` - Swagger/OpenAPI docs
- `django-cors-headers==4.3.1` - CORS support
- `django-mongodb-backend==5.2.3` - MongoDB support
- `python-dotenv==1.0.0` - Environment config

### 2. Configure Environment

Copy `.env.example` to `.env` and update values:

```bash
cp .env.example .env
```

Edit `.env`:
```env
DEBUG=True
SECRET_KEY=your-secret-key-here

# Database
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/database

# Email
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend  # Use for development
# For production, use SMTP backend with Gmail or other provider

# Frontend URLs
FRONTEND_URL=http://localhost:3000
FRONTEND_RESET_PASSWORD_URL=http://localhost:3000/reset-password
FRONTEND_ACTIVATE_ACCOUNT_URL=http://localhost:3000/activate
```

### 3. Run Migrations

```bash
python manage.py migrate
```

### 4. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 5. Start Development Server

```bash
python manage.py runserver
```

Visit:
- API: `http://localhost:8000/api/`
- Swagger Docs: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`
- Admin: `http://localhost:8000/admin/`

---

## 🔐 Authentication Endpoints

All endpoints are prefixed with `/api/auth/`

### 1. Register User
**Endpoint:** `POST /api/auth/register/`

**Request:**
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "SecurePassword123!",
  "password_confirm": "SecurePassword123!"
}
```

**Response (201):**
```json
{
  "detail": "User registered successfully. Please check your email to verify your account.",
  "email": "user@example.com"
}
```

**Error (400):**
```json
{
  "email": ["This email is already registered."],
  "password": ["Password too short"]
}
```

**Notes:**
- Passwords must be at least 8 characters
- Passwords are validated against Django's password validators
- Verification email is sent automatically
- User account is **inactive** until email is verified

---

### 2. Verify Email (Activate Account)
**Endpoint:** `POST /api/auth/activate/`

**Request:**
```json
{
  "uid": "MTA=",
  "token": "5aq-2d8d5c5e5c5c5c5c5c5c5c5c"
}
```

Note: `uid` and `token` are provided in the email verification link

**Response (200):**
```json
{
  "detail": "Email verified successfully. Your account is now active.",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "user@example.com",
    "name": "John Doe",
    "is_active": true,
    "is_staff": false,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:35:00Z"
  }
}
```

---

### 3. Login (Get JWT Tokens)
**Endpoint:** `POST /api/auth/login/`

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200):**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "user@example.com",
    "name": "John Doe",
    "is_active": true,
    "is_staff": false,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:35:00Z"
  }
}
```

**Error (400):**
```json
{
  "detail": "This account is not active. Please verify your email."
}
```

---

### 4. Refresh Access Token
**Endpoint:** `POST /api/auth/token/refresh/`

**Request:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

### 5. Get Current User
**Endpoint:** `GET /api/auth/me/`

**Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

**Response (200):**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "email": "user@example.com",
  "name": "John Doe",
  "is_active": true,
  "is_staff": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:35:00Z"
}
```

---

### 6. Change Password
**Endpoint:** `POST /api/auth/change-password/`

**Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

**Request:**
```json
{
  "old_password": "SecurePassword123!",
  "new_password": "NewPassword456!",
  "new_password_confirm": "NewPassword456!"
}
```

**Response (200):**
```json
{
  "detail": "Password changed successfully."
}
```

---

### 7. Forgot Password
**Endpoint:** `POST /api/auth/forgot-password/`

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response (200):**
```json
{
  "detail": "If a user with this email exists, a password reset link has been sent."
}
```

**Note:** Returns same message for all cases (security - prevents user enumeration)

---

### 8. Reset Password
**Endpoint:** `POST /api/auth/reset-password/`

**Request:**
```json
{
  "uid": "MTA=",
  "token": "5aq-2d8d5c5e5c5c5c5c5c5c5c5c",
  "new_password": "NewPassword456!",
  "new_password_confirm": "NewPassword456!"
}
```

**Response (200):**
```json
{
  "detail": "Password reset successfully. You can now login with your new password."
}
```

---

### 9. Logout
**Endpoint:** `POST /api/auth/logout/`

**Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

**Response (200):**
```json
{
  "detail": "Logged out successfully."
}
```

---

## 🔑 JWT Token Structure

### Access Token
- **Lifetime:** 15 minutes (configurable)
- **Used for:** Authenticating API requests
- **Header:** `Authorization: Bearer {access_token}`

### Refresh Token
- **Lifetime:** 7 days (configurable)
- **Used for:** Getting a new access token
- **Rotation:** Enabled (old refresh tokens are blacklisted)

### Token Claims
```json
{
  "token_type": "access",
  "exp": 1705311600,
  "iat": 1705310700,
  "jti": "abc123...",
  "user_id": "507f1f77bcf86cd799439011",
  "username": "user@example.com"
}
```

---

## 🛡️ Security Features

### ✅ Password Security
- Passwords hashed using Django's PBKDF2 algorithm
- Password strength validation (min 8 characters)
- Common password blacklist
- User attribute similarity check

### ✅ Token Security
- HMAC-SHA256 signing
- Token expiration
- Refresh token rotation
- Optional token blacklist

### ✅ User Enumeration Prevention
- Forgot password returns same message for all cases
- No user existence leaks

### ✅ Email Verification
- Secure token generation
- 24-hour expiration
- One-time use per token

### ✅ CORS Security
- Whitelist allowed origins
- Credentials enabled

---

## 📧 Email Configuration

### Development (Console Backend)
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```
Emails print to console.

### Production (Gmail)
1. Enable 2-factor authentication on Gmail
2. Generate app password: https://myaccount.google.com/apppasswords
3. Configure in `.env`:
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password
```

### Custom SMTP Server
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=your-smtp-server.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-username
EMAIL_HOST_PASSWORD=your-password
```

---

## 📚 Project Structure

```
quickstart/
├── authentication/          # Auth app
│   ├── views.py            # API endpoints
│   ├── serializers.py      # Request/response validators
│   ├── utils.py            # Email, token utilities
│   ├── urls.py             # Route definitions
│   ├── apps.py             # App config
│   └── templates/          # Email templates
│       └── emails/
│           ├── verify_email.html
│           └── reset_password.html
├── users/                  # User app
│   ├── models.py           # Custom User model
│   ├── admin.py            # Admin interface
│   ├── apps.py             # App config
│   └── migrations/         # Database migrations
├── quickstart/             # Project config
│   ├── settings.py         # Django settings
│   ├── urls.py             # Main URL routing
│   └── wsgi.py             # WSGI config
├── .env                    # Environment variables
├── .env.example            # Example env file
├── manage.py               # Django CLI
└── requirements.txt        # Python dependencies
```

---

## 🧪 Testing the API

### Using cURL

**Register:**
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "password": "TestPassword123!",
    "password_confirm": "TestPassword123!"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }'
```

**Get Me (Authenticated):**
```bash
curl -X GET http://localhost:8000/api/auth/me/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Using Postman
1. Import the Swagger schema: `http://localhost:8000/api/schema/`
2. Create environment variables:
   - `base_url`: `http://localhost:8000`
   - `access_token`: Paste token from login response
   - `refresh_token`: Paste token from login response
3. Use pre-built endpoints to test

### Using Python Requests
```python
import requests

BASE_URL = 'http://localhost:8000/api/auth'

# Register
response = requests.post(f'{BASE_URL}/register/', json={
    'email': 'test@example.com',
    'name': 'Test User',
    'password': 'TestPassword123!',
    'password_confirm': 'TestPassword123!'
})
print(response.json())

# Login
response = requests.post(f'{BASE_URL}/login/', json={
    'email': 'test@example.com',
    'password': 'TestPassword123!'
})
tokens = response.json()
access_token = tokens['access']

# Get Me
response = requests.get(
    f'{BASE_URL}/me/',
    headers={'Authorization': f'Bearer {access_token}'}
)
print(response.json())
```

---

## 🚀 Deployment Checklist

- [ ] Set `DEBUG=False` in production
- [ ] Generate new `SECRET_KEY` for production
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Set `SECURE_SSL_REDIRECT=True`
- [ ] Set `SESSION_COOKIE_SECURE=True`
- [ ] Set `CSRF_COOKIE_SECURE=True`
- [ ] Configure email backend with production SMTP server
- [ ] Set `CORS_ALLOWED_ORIGINS` to your frontend domain
- [ ] Use strong database credentials
- [ ] Enable HTTPS/SSL certificate
- [ ] Set up logging and monitoring
- [ ] Configure backups for database
- [ ] Use environment variables for sensitive data
- [ ] Run security checks: `python manage.py check --deploy`
- [ ] Enable rate limiting for auth endpoints
- [ ] Set up monitoring alerts for auth failures

---

## 🐛 Troubleshooting

### Issue: "No module named 'rest_framework_simplejwt'"
**Solution:** Run `pip install -r requirements.txt`

### Issue: "collection django_content_type already exists"
**Solution:** Drop existing collections in MongoDB and run migrations fresh

### Issue: Email not received
**Solution:**
1. Check `EMAIL_BACKEND` is set correctly
2. For Gmail: Use app password, not regular password
3. Check Django logs for email send errors
4. Verify `DEFAULT_FROM_EMAIL` is valid

### Issue: CORS errors
**Solution:**
1. Check `CORS_ALLOWED_ORIGINS` includes your frontend domain
2. Verify frontend makes requests with credentials: `credentials: 'include'`
3. Check browser console for specific CORS error

### Issue: "Invalid token" on refresh
**Solution:**
1. Token might have expired (check expiry time)
2. Database might have been cleared (refresh tokens are stored)
3. Try logging in again to get new tokens

---

## 📖 Additional Resources

- [Django REST Framework Docs](https://www.django-rest-framework.org/)
- [djangorestframework-simplejwt Docs](https://django-rest-framework-simplejwt.readthedocs.io/)
- [Django Security Docs](https://docs.djangoproject.com/en/stable/topics/security/)
- [JWT.io](https://jwt.io/) - JWT debugger
- [drf-spectacular Docs](https://drf-spectacular.readthedocs.io/)

---

## 📝 License

This authentication system is provided as-is for educational and production use.

---

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the API Examples file (`API_EXAMPLES.md`)
3. Check Django/DRF logs: `tail -f logs/debug.log`
4. Review error responses for specific error messages


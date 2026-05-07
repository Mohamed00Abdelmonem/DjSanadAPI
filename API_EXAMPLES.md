# ============================================================================
# AUTHENTICATION API - EXAMPLE REQUESTS & RESPONSES
# ============================================================================
# 
# This file contains curl examples for all authentication endpoints.
# Replace localhost:8000 with your actual API URL.
#

# ============================================================================
# 1. REGISTER - Create new user account
# ============================================================================

curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "name": "John Doe",
    "password": "SecurePassword123!",
    "password_confirm": "SecurePassword123!"
  }'

# SUCCESS RESPONSE (201):
{
  "detail": "User registered successfully. Please check your email to verify your account.",
  "email": "john@example.com"
}

# ERROR RESPONSES:
# 400 - Validation errors
{
  "email": ["This email is already registered."],
  "password": ["Password too short"]
}

---

# ============================================================================
# 2. EMAIL VERIFICATION - Activate account
# ============================================================================
# Get uid and token from the email verification link

curl -X POST http://localhost:8000/api/auth/activate/ \
  -H "Content-Type: application/json" \
  -d '{
    "uid": "base64-encoded-user-id",
    "token": "verification-token-from-email"
  }'

# SUCCESS RESPONSE (200):
{
  "detail": "Email verified successfully. Your account is now active.",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "john@example.com",
    "name": "John Doe",
    "is_active": true,
    "is_staff": false,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:35:00Z"
  }
}

# ERROR RESPONSES:
# 400 - Invalid token
{
  "detail": "Invalid or expired verification token."
}

---

# ============================================================================
# 3. LOGIN - Get JWT tokens
# ============================================================================

curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePassword123!"
  }'

# SUCCESS RESPONSE (200):
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "john@example.com",
    "name": "John Doe",
    "is_active": true,
    "is_staff": false,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:35:00Z"
  }
}

# ERROR RESPONSES:
# 401 - Invalid credentials
{
  "detail": "No active account found with the given credentials"
}

# 400 - Account not active
{
  "detail": "This account is not active. Please verify your email."
}

---

# ============================================================================
# 4. TOKEN REFRESH - Get new access token
# ============================================================================

curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }'

# SUCCESS RESPONSE (200):
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}

# ERROR RESPONSES:
# 401 - Invalid refresh token
{
  "detail": "Token is invalid or expired"
}

---

# ============================================================================
# 5. GET ME - Get current authenticated user info
# ============================================================================

curl -X GET http://localhost:8000/api/auth/me/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

# SUCCESS RESPONSE (200):
{
  "id": "507f1f77bcf86cd799439011",
  "email": "john@example.com",
  "name": "John Doe",
  "is_active": true,
  "is_staff": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:35:00Z"
}

# ERROR RESPONSES:
# 401 - Unauthorized
{
  "detail": "Authentication credentials were not provided."
}

---

# ============================================================================
# 6. CHANGE PASSWORD - Change password for authenticated user
# ============================================================================

curl -X POST http://localhost:8000/api/auth/change-password/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -d '{
    "old_password": "SecurePassword123!",
    "new_password": "NewSecurePassword456!",
    "new_password_confirm": "NewSecurePassword456!"
  }'

# SUCCESS RESPONSE (200):
{
  "detail": "Password changed successfully."
}

# ERROR RESPONSES:
# 400 - Old password incorrect
{
  "old_password": ["Old password is incorrect."]
}

# 400 - Passwords don't match
{
  "new_password": ["Password fields didn't match."]
}

---

# ============================================================================
# 7. FORGOT PASSWORD - Request password reset email
# ============================================================================

curl -X POST http://localhost:8000/api/auth/forgot-password/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com"
  }'

# SUCCESS RESPONSE (200):
# Note: Always returns 200 and same message for security (no user enumeration)
{
  "detail": "If a user with this email exists, a password reset link has been sent."
}

---

# ============================================================================
# 8. RESET PASSWORD - Reset password with token from email
# ============================================================================

curl -X POST http://localhost:8000/api/auth/reset-password/ \
  -H "Content-Type: application/json" \
  -d '{
    "uid": "base64-encoded-user-id",
    "token": "reset-token-from-email",
    "new_password": "NewSecurePassword456!",
    "new_password_confirm": "NewSecurePassword456!"
  }'

# SUCCESS RESPONSE (200):
{
  "detail": "Password reset successfully. You can now login with your new password."
}

# ERROR RESPONSES:
# 400 - Invalid token
{
  "detail": "Invalid or expired reset token."
}

# 400 - Passwords don't match
{
  "new_password": ["Password fields didn't match."]
}

---

# ============================================================================
# 9. LOGOUT - Logout user (optional endpoint for tracking)
# ============================================================================

curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

# SUCCESS RESPONSE (200):
{
  "detail": "Logged out successfully."
}

---

# ============================================================================
# API DOCUMENTATION
# ============================================================================

# Swagger UI: http://localhost:8000/api/docs/
# ReDoc: http://localhost:8000/api/redoc/
# OpenAPI Schema: http://localhost:8000/api/schema/

---

# ============================================================================
# ACTIVITIES API - EXAMPLE REQUESTS & RESPONSES
# ============================================================================

# NOTE: All activities endpoints require JWT authentication
# Authorization: Bearer <access_token>

# ============================================================================
# 1. CREATE ACTIVITY (Admin only)
# ============================================================================

curl -X POST http://localhost:8000/api/activities/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Deep Breathing",
    "description": "Helps reduce stress",
    "category": "breathing",
    "time_takes": 5,
    "emoji": "\ud83e\uddd8",
    "steps": [
      "Sit comfortably",
      "Close your eyes",
      "Take a deep breath"
    ]
  }'

# SUCCESS RESPONSE (201):
{
  "id": "507f1f77bcf86cd799439012",
  "name": "Deep Breathing",
  "description": "Helps reduce stress",
  "category": "breathing",
  "time_takes": 5,
  "emoji": "\ud83e\uddd8",
  "steps": [
    "Sit comfortably",
    "Close your eyes",
    "Take a deep breath"
  ],
  "average_rating": 0.0,
  "total_ratings": 0
}

# ============================================================================
# 2. LIST ACTIVITIES (Authenticated users only)
# ============================================================================

curl -X GET "http://localhost:8000/api/activities/?category=breathing" \
  -H "Authorization: Bearer <access_token>"

# SUCCESS RESPONSE (200):
[
  {
    "id": "507f1f77bcf86cd799439012",
    "name": "Deep Breathing",
    "description": "Helps reduce stress",
    "category": "breathing",
    "time_takes": 5,
    "emoji": "\ud83e\uddd8",
    "steps": [
      "Sit comfortably",
      "Close your eyes",
      "Take a deep breath"
    ],
    "average_rating": 4.8,
    "total_ratings": 120
  }
]

# ============================================================================
# 3. GET ACTIVITY DETAIL
# ============================================================================

curl -X GET http://localhost:8000/api/activities/507f1f77bcf86cd799439012/ \
  -H "Authorization: Bearer <access_token>"

# SUCCESS RESPONSE (200):
{
  "id": "507f1f77bcf86cd799439012",
  "name": "Deep Breathing",
  "description": "Helps reduce stress",
  "category": "breathing",
  "time_takes": 5,
  "emoji": "\ud83e\uddd8",
  "steps": [
    "Sit comfortably",
    "Close your eyes",
    "Take a deep breath"
  ],
  "average_rating": 4.8,
  "total_ratings": 120
}

# ============================================================================
# 4. UPDATE ACTIVITY (Admin only)
# ============================================================================

curl -X PATCH http://localhost:8000/api/activities/507f1f77bcf86cd799439012/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "time_takes": 6,
    "steps": [
      "Sit comfortably",
      "Close your eyes",
      "Take a deep breath",
      "Exhale slowly"
    ]
  }'

# SUCCESS RESPONSE (200):
{
  "id": "507f1f77bcf86cd799439012",
  "name": "Deep Breathing",
  "description": "Helps reduce stress",
  "category": "breathing",
  "time_takes": 6,
  "emoji": "\ud83e\uddd8",
  "steps": [
    "Sit comfortably",
    "Close your eyes",
    "Take a deep breath",
    "Exhale slowly"
  ],
  "average_rating": 4.8,
  "total_ratings": 120
}

# ============================================================================
# 5. DELETE ACTIVITY (Admin only - Soft delete)
# ============================================================================

curl -X DELETE http://localhost:8000/api/activities/507f1f77bcf86cd799439012/ \
  -H "Authorization: Bearer <access_token>"

# SUCCESS RESPONSE (204):
# No content. The activity is soft deleted and will not appear in lists.

# ============================================================================
# 6. RATE ACTIVITY (Authenticated users only)
# ============================================================================

curl -X POST http://localhost:8000/api/activities/507f1f77bcf86cd799439012/rate/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "rate": 5
  }'

# SUCCESS RESPONSE (200):
{
  "id": "507f1f77bcf86cd799439012",
  "name": "Deep Breathing",
  "description": "Helps reduce stress",
  "category": "breathing",
  "time_takes": 6,
  "emoji": "\ud83e\uddd8",
  "steps": [
    "Sit comfortably",
    "Close your eyes",
    "Take a deep breath",
    "Exhale slowly"
  ],
  "average_rating": 4.9,
  "total_ratings": 121
}

---

# ============================================================================
# AUTHENTICATION FLOW
# ============================================================================

# 1. User registers:
#    POST /api/auth/register/
#    → Receives verification email
#
# 2. User verifies email:
#    POST /api/auth/activate/
#    → Account is now active
#
# 3. User logs in:
#    POST /api/auth/login/
#    → Receives access and refresh tokens
#
# 4. User uses access token for authenticated requests:
#    GET /api/auth/me/
#    Header: Authorization: Bearer {access_token}
#
# 5. When access token expires, use refresh token:
#    POST /api/auth/token/refresh/
#    → Receives new access token
#
# 6. User can change password:
#    POST /api/auth/change-password/
#
# 7. User can reset forgotten password:
#    POST /api/auth/forgot-password/
#    → Receives reset email
#    POST /api/auth/reset-password/
#    → Password is reset

---

# ============================================================================
# COMMON HTTP STATUS CODES
# ============================================================================

# 200 - OK
# 201 - Created
# 400 - Bad Request (validation error)
# 401 - Unauthorized (invalid/missing credentials)
# 403 - Forbidden (authenticated but no permission)
# 404 - Not Found
# 500 - Server Error

---

# ============================================================================
# USEFUL CURL OPTIONS
# ============================================================================

# Pretty print JSON response:
# ... | python -m json.tool

# Save response to file:
# ... > response.json

# Show headers:
# curl -i http://localhost:8000/api/auth/me/

# Verbose mode (show request and response):
# curl -v http://localhost:8000/api/auth/me/

# Save cookie (for session-based auth, not needed for JWT):
# curl -c cookies.txt http://localhost:8000/api/auth/login/

---

# ============================================================================
# ENVIRONMENT SETUP
# ============================================================================

# Create .env file with:
# EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend  # For testing
# EMAIL_HOST=smtp.gmail.com  # For production
# EMAIL_HOST_USER=your-email@gmail.com
# EMAIL_HOST_PASSWORD=your-app-password
# FRONTEND_URL=http://localhost:3000
# FRONTEND_RESET_PASSWORD_URL=http://localhost:3000/reset-password
# FRONTEND_ACTIVATE_ACCOUNT_URL=http://localhost:3000/activate

# Generate SECRET_KEY:
# python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

---

# ============================================================================
# TROUBLESHOOTING
# ============================================================================

# 1. Email not received?
#    - Check EMAIL_BACKEND in settings (should be SMTP for production)
#    - Check Django logs: tail -f logs/debug.log
#    - Use Gmail app password, not regular password
#
# 2. Token invalid?
#    - Make sure token hasn't expired (check JWT_ACCESS_TOKEN_LIFETIME)
#    - Make sure Bearer prefix is included
#    - Token format: "Bearer {token}"
#
# 3. User can't activate?
#    - Email verification link might have expired
#    - Request forgot password to reset
#
# 4. CORS errors?
#    - Check CORS_ALLOWED_ORIGINS in settings.py
#    - Make sure frontend URL is in the list


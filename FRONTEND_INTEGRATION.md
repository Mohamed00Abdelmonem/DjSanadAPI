# Frontend Integration Guide

## 🎯 How to Use JWT Tokens in Frontend

### React Example

```javascript
// api.js - Axios instance with JWT
import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Include cookies
});

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle token refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refresh = localStorage.getItem('refresh_token');
        const response = await axios.post(
          `${API_URL}/auth/token/refresh/`,
          { refresh }
        );
        
        localStorage.setItem('access_token', response.data.access);
        originalRequest.headers.Authorization = `Bearer ${response.data.access}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export default api;
```

### Register Component

```javascript
// Register.jsx
import { useState } from 'react';
import api from './api';

export default function Register() {
  const [formData, setFormData] = useState({
    email: '',
    name: '',
    password: '',
    password_confirm: '',
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setMessage('');

    try {
      const response = await api.post('/auth/register/', formData);
      setMessage(response.data.detail);
      setFormData({
        email: '',
        name: '',
        password: '',
        password_confirm: '',
      });
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        name="email"
        placeholder="Email"
        value={formData.email}
        onChange={handleChange}
        required
      />
      <input
        type="text"
        name="name"
        placeholder="Full Name"
        value={formData.name}
        onChange={handleChange}
        required
      />
      <input
        type="password"
        name="password"
        placeholder="Password"
        value={formData.password}
        onChange={handleChange}
        required
      />
      <input
        type="password"
        name="password_confirm"
        placeholder="Confirm Password"
        value={formData.password_confirm}
        onChange={handleChange}
        required
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Registering...' : 'Register'}
      </button>
      {message && <p className="success">{message}</p>}
      {error && <p className="error">{error}</p>}
    </form>
  );
}
```

### Login Component

```javascript
// Login.jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from './api';

export default function Login() {
  const navigate = useNavigate();
  const [credentials, setCredentials] = useState({
    email: '',
    password: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setCredentials(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await api.post('/auth/login/', credentials);
      
      // Store tokens
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
      localStorage.setItem('user', JSON.stringify(response.data.user));
      
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        name="email"
        placeholder="Email"
        value={credentials.email}
        onChange={handleChange}
        required
      />
      <input
        type="password"
        name="password"
        placeholder="Password"
        value={credentials.password}
        onChange={handleChange}
        required
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
      {error && <p className="error">{error}</p>}
    </form>
  );
}
```

### Email Verification Component

```javascript
// EmailVerification.jsx
import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import api from './api';

export default function EmailVerification() {
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState('verifying');
  const [message, setMessage] = useState('');

  useEffect(() => {
    const verifyEmail = async () => {
      const uid = searchParams.get('uid');
      const token = searchParams.get('token');

      try {
        const response = await api.post('/auth/activate/', { uid, token });
        setStatus('success');
        setMessage(response.data.detail);
      } catch (err) {
        setStatus('error');
        setMessage(err.response?.data?.detail || 'Verification failed');
      }
    };

    if (searchParams.get('uid') && searchParams.get('token')) {
      verifyEmail();
    }
  }, [searchParams]);

  return (
    <div>
      {status === 'verifying' && <p>Verifying your email...</p>}
      {status === 'success' && (
        <>
          <p className="success">{message}</p>
          <a href="/login">Go to Login</a>
        </>
      )}
      {status === 'error' && <p className="error">{message}</p>}
    </div>
  );
}
```

### Protected Route Component

```javascript
// ProtectedRoute.jsx
import { Navigate } from 'react-router-dom';

export default function ProtectedRoute({ children }) {
  const token = localStorage.getItem('access_token');

  if (!token) {
    return <Navigate to="/login" />;
  }

  return children;
}

// Usage
<Route
  path="/dashboard"
  element={
    <ProtectedRoute>
      <Dashboard />
    </ProtectedRoute>
  }
/>
```

---

## 🔌 Fetch Example (No External Libraries)

```javascript
// Using native Fetch API
const API_URL = 'http://localhost:8000/api/auth';

async function login(email, password) {
  const response = await fetch(`${API_URL}/login/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    throw new Error('Login failed');
  }

  const data = await response.json();
  localStorage.setItem('access_token', data.access);
  localStorage.setItem('refresh_token', data.refresh);
  return data;
}

async function getMe() {
  const token = localStorage.getItem('access_token');
  const response = await fetch(`${API_URL}/me/`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
    credentials: 'include',
  });

  if (!response.ok) {
    throw new Error('Failed to get user');
  }

  return await response.json();
}
```

---

## 📱 Vue.js Example

```javascript
// composables/useAuth.js
import { ref, computed } from 'vue';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/auth';
const accessToken = ref(localStorage.getItem('access_token'));
const user = ref(JSON.parse(localStorage.getItem('user') || 'null'));

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use(config => {
  if (accessToken.value) {
    config.headers.Authorization = `Bearer ${accessToken.value}`;
  }
  return config;
});

export function useAuth() {
  const isAuthenticated = computed(() => !!accessToken.value);

  async function register(email, name, password) {
    const response = await api.post('/register/', {
      email,
      name,
      password,
      password_confirm: password,
    });
    return response.data;
  }

  async function login(email, password) {
    const response = await api.post('/login/', { email, password });
    accessToken.value = response.data.access;
    user.value = response.data.user;
    localStorage.setItem('access_token', response.data.access);
    localStorage.setItem('refresh_token', response.data.refresh);
    localStorage.setItem('user', JSON.stringify(response.data.user));
    return response.data;
  }

  async function logout() {
    accessToken.value = null;
    user.value = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  }

  return {
    accessToken,
    user,
    isAuthenticated,
    register,
    login,
    logout,
  };
}
```

---

## 🌍 CORS Configuration

Make sure your frontend domain is whitelisted in Django settings:

```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',  # Development
    'https://yourdomain.com',  # Production
]

CORS_ALLOW_CREDENTIALS = True
```

---

## 🔄 Token Refresh Strategy

The tokens have these lifetimes:
- **Access Token:** 15 minutes
- **Refresh Token:** 7 days

**Automatic Refresh Strategy:**
1. Make API request with access token
2. If 401 (Unauthorized), use refresh token to get new access token
3. Retry original request with new token
4. If refresh fails, redirect to login

See the Axios example above for implementation.

---

## 📦 Environment Variables for Frontend

Create `.env.local` in your frontend:

```
VITE_API_URL=http://localhost:8000
VITE_API_AUTH_URL=http://localhost:8000/api/auth
```

Usage:
```javascript
const API_URL = import.meta.env.VITE_API_URL;
```


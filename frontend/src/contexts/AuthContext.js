import { createContext, useContext, useState, useEffect, useCallback, useMemo } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

const API_URL = process.env.REACT_APP_BACKEND_URL;

const ACCESS_KEY = 'rtn_access_token';
const REFRESH_KEY = 'rtn_refresh_token';
const SESSION_IDLE_MS = 30 * 60 * 1000; // 30 minutes

// Always send cookies (same-origin) AND restore a stored bearer token on load,
// so auth survives environments where cross-site cookies are blocked (mobile/PWA).
// Using sessionStorage so tokens clear when the browser session ends (tab close).
axios.defaults.withCredentials = true;
const savedAccess = sessionStorage.getItem(ACCESS_KEY);
if (savedAccess) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${savedAccess}`;
}

function setTokens(access, refresh) {
  if (access) {
    sessionStorage.setItem(ACCESS_KEY, access);
    axios.defaults.headers.common['Authorization'] = `Bearer ${access}`;
  }
  if (refresh) {
    sessionStorage.setItem(REFRESH_KEY, refresh);
  }
}

function clearTokens() {
  sessionStorage.removeItem(ACCESS_KEY);
  sessionStorage.removeItem(REFRESH_KEY);
  delete axios.defaults.headers.common['Authorization'];
}

// Auto-refresh the access token on 401 (once), using the stored refresh token.
let isRefreshing = false;
let refreshPromise = null;
axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    const status = error.response?.status;
    const url = original?.url || '';
    const isAuthCall =
      url.includes('/api/auth/login') ||
      url.includes('/api/auth/refresh') ||
      url.includes('/api/auth/register') ||
      url.includes('/api/auth/logout');

    if (status === 401 && original && !original._retry && !isAuthCall) {
      const refresh = sessionStorage.getItem(REFRESH_KEY);
      if (!refresh) return Promise.reject(error);
      original._retry = true;
      try {
        if (!isRefreshing) {
          isRefreshing = true;
          refreshPromise = axios
            .post(`${API_URL}/api/auth/refresh`, { refresh_token: refresh }, { withCredentials: true })
            .then((res) => {
              setTokens(res.data.access_token, res.data.refresh_token);
              return res.data.access_token;
            })
            .finally(() => {
              isRefreshing = false;
            });
        }
        const newAccess = await refreshPromise;
        if (newAccess) {
          original.headers = original.headers || {};
          original.headers['Authorization'] = `Bearer ${newAccess}`;
        }
        return axios(original);
      } catch (refreshErr) {
        clearTokens();
        return Promise.reject(error);
      }
    }
    return Promise.reject(error);
  }
);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const checkAuth = useCallback(async () => {
    try {
      const response = await axios.get(`${API_URL}/api/auth/me`, { withCredentials: true });
      setUser(response.data);
    } catch (error) {
      setUser(false);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  // logout declared here so the auto-sign-out useEffect below can reference it without TDZ issues
  const logout = useCallback(async () => {
    try {
      await axios.post(`${API_URL}/api/auth/logout`, {}, { withCredentials: true });
    } catch (_) { /* ignore */ }
    clearTokens();
    sessionStorage.removeItem('ws_token');
    setUser(false);
  }, []);

  // Auto sign-out: after 30 minutes hidden (tab switched / app backgrounded)
  useEffect(() => {
    if (!user) return;
    let idleTimer = null;
    const onVisibilityChange = () => {
      if (document.hidden) {
        idleTimer = setTimeout(() => {
          logout();
        }, SESSION_IDLE_MS);
      } else {
        if (idleTimer) { clearTimeout(idleTimer); idleTimer = null; }
      }
    };
    document.addEventListener('visibilitychange', onVisibilityChange);
    return () => {
      document.removeEventListener('visibilitychange', onVisibilityChange);
      if (idleTimer) clearTimeout(idleTimer);
    };
  }, [user, logout]);

  const login = useCallback(async (email, password) => {
    const response = await axios.post(
      `${API_URL}/api/auth/login`,
      { email, password },
      { withCredentials: true }
    );
    // 2FA required — return challenge to caller, do NOT set user
    if (response.data?.two_factor_required) {
      return { twoFactorRequired: true, challengeToken: response.data.challenge_token };
    }
    setTokens(response.data.access_token, response.data.refresh_token);
    if (response.data.id) {
      sessionStorage.setItem('ws_token', response.data.id);
    }
    setUser(response.data);
    return response.data;
  }, []);

  const loginVerify2FA = useCallback(async (challengeToken, code, recoveryCode) => {
    const body = { challenge_token: challengeToken };
    if (code) body.code = code;
    if (recoveryCode) body.recovery_code = recoveryCode;
    const response = await axios.post(`${API_URL}/api/auth/login/2fa`, body, { withCredentials: true });
    setTokens(response.data.access_token, response.data.refresh_token);
    if (response.data.id) {
      sessionStorage.setItem('ws_token', response.data.id);
    }
    setUser(response.data);
    return response.data;
  }, []);

  const register = useCallback(async (email, password, name, location, invite_token) => {
    const response = await axios.post(
      `${API_URL}/api/auth/register`,
      { email, password, name, location, invite_token },
      { withCredentials: true }
    );
    setTokens(response.data.access_token, response.data.refresh_token);
    if (response.data.id) {
      sessionStorage.setItem('ws_token', response.data.id);
    }
    setUser(response.data);
    return response.data;
  }, []);

  const updateUser = useCallback((userData) => {
    setUser((prev) => ({ ...prev, ...userData }));
  }, []);

  const value = useMemo(
    () => ({ user, loading, login, loginVerify2FA, register, logout, updateUser, checkAuth }),
    [user, loading, login, loginVerify2FA, register, logout, updateUser, checkAuth]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

import { createContext, useContext, useState, useEffect, useCallback, useMemo } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

const API_URL = process.env.REACT_APP_BACKEND_URL;

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const checkAuth = useCallback(async () => {
    try {
      const response = await axios.get(`${API_URL}/api/auth/me`, {
        withCredentials: true
      });
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
    const response = await axios.post(
      `${API_URL}/api/auth/login/2fa`,
      body,
      { withCredentials: true }
    );
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
    // Store user ID for WebSocket auth
    if (response.data.id) {
      sessionStorage.setItem('ws_token', response.data.id);
    }
    setUser(response.data);
    return response.data;
  }, []);

  const logout = useCallback(async () => {
    await axios.post(`${API_URL}/api/auth/logout`, {}, { withCredentials: true });
    sessionStorage.removeItem('ws_token');
    setUser(false);
  }, []);

  const updateUser = useCallback((userData) => {
    setUser(prev => ({ ...prev, ...userData }));
  }, []);

  const value = useMemo(() => ({
    user,
    loading,
    login,
    loginVerify2FA,
    register,
    logout,
    updateUser,
    checkAuth
  }), [user, loading, login, loginVerify2FA, register, logout, updateUser, checkAuth]);

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

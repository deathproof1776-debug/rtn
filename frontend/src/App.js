import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import { WebSocketProvider } from "./contexts/WebSocketContext";
import { NotificationProvider } from "./contexts/NotificationContext";
import { ThemeProvider } from "./contexts/ThemeContext";
import { PWAProvider } from "./contexts/PWAContext";
import { Toaster } from "./components/ui/sonner";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0C0A09] flex items-center justify-center">
        <div className="text-[#A8A29E]">Loading...</div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <WebSocketProvider>
      <NotificationProvider>
        {children}
      </NotificationProvider>
    </WebSocketProvider>
  );
}

function PublicRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0C0A09] flex items-center justify-center">
        <div className="text-[#A8A29E]">Loading...</div>
      </div>
    );
  }

  if (user) {
    return <Navigate to="/" replace />;
  }

  return children;
}

function AppRoutes() {
  return (
    <Routes>
      <Route
        path="/login"
        element={
          <PublicRoute>
            <Login />
          </PublicRoute>
        }
      />
      <Route
        path="/register"
        element={
          <PublicRoute>
            <Register />
          </PublicRoute>
        }
      />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

import { useEffect } from "react";

function App() {
  // Set environment attribute for CSS watermark clearance
  useEffect(() => {
    const hostname = window.location.hostname;
    const isPreview = hostname.includes('.preview.emergentagent.com');
    document.documentElement.setAttribute('data-env', isPreview ? 'preview' : 'deployed');
  }, []);

  return (
    <div className="App">
      <ThemeProvider>
        <PWAProvider>
          <AuthProvider>
            <BrowserRouter>
              <AppRoutes />
              <Toaster />
            </BrowserRouter>
          </AuthProvider>
        </PWAProvider>
      </ThemeProvider>
    </div>
  );
}

export default App;

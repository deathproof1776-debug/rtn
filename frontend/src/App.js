import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import { WebSocketProvider } from "./contexts/WebSocketContext";
import { NotificationProvider } from "./contexts/NotificationContext";
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

function App() {
  return (
    <div className="App">
      <AuthProvider>
        <BrowserRouter>
          <AppRoutes />
          <Toaster />
        </BrowserRouter>
      </AuthProvider>
    </div>
  );
}

export default App;

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Shield, Eye, EyeSlash, ArrowRight } from '@phosphor-icons/react';

function formatApiErrorDetail(detail) {
  if (detail == null) return "Something went wrong. Please try again.";
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail))
    return detail.map((e) => (e && typeof e.msg === "string" ? e.msg : JSON.stringify(e))).filter(Boolean).join(" ");
  if (detail && typeof detail.msg === "string") return detail.msg;
  return String(detail);
}

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password);
      navigate('/');
    } catch (err) {
      setError(formatApiErrorDetail(err.response?.data?.detail) || err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center relative" 
         style={{ 
           backgroundImage: 'url(https://images.unsplash.com/photo-1604549001484-df28edea610b?crop=entropy&cs=srgb&fm=jpg&q=85)',
           backgroundSize: 'cover',
           backgroundPosition: 'center'
         }}>
      <div className="absolute inset-0 bg-black/70"></div>
      
      <div className="relative z-10 w-full max-w-md p-8 animate-fade-in">
        <div className="bg-[var(--bg-surface)] border border-[var(--bg-surface-active)] border-t-[3px] border-t-[var(--brand-primary)] p-8">
          <div className="flex items-center gap-3 mb-8">
            <Shield size={40} weight="duotone" className="text-[var(--brand-primary)]" />
            <div>
              <h1 className="text-2xl font-black tracking-tight text-[var(--text-primary)]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
                REBEL TRADE NETWORK
              </h1>
              <p className="text-xs uppercase tracking-[0.2em] text-[var(--text-muted)]">Exit the Matrix</p>
            </div>
          </div>

          <h2 className="text-xl font-semibold text-[var(--text-primary)] mb-6">Welcome Back</h2>

          {error && (
            <div className="bg-[var(--brand-danger)]/20 border border-[var(--brand-danger)] text-[var(--text-primary)] px-4 py-3 mb-6" data-testid="login-error">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm text-[var(--text-secondary)] mb-2">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input-field w-full"
                placeholder="you@homestead.com"
                required
                data-testid="login-email-input"
              />
            </div>

            <div>
              <label className="block text-sm text-[var(--text-secondary)] mb-2">Password</label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="input-field w-full pr-10"
                  placeholder="Enter your password"
                  required
                  data-testid="login-password-input"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--text-muted)] hover:text-[var(--text-primary)]"
                >
                  {showPassword ? <EyeSlash size={20} /> : <Eye size={20} />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full flex items-center justify-center gap-2"
              data-testid="login-submit-button"
            >
              {loading ? 'Signing in...' : (
                <>
                  Enter the Network
                  <ArrowRight size={20} weight="bold" />
                </>
              )}
            </button>
          </form>

          <p className="mt-6 text-center text-[var(--text-muted)] text-sm">
            Rebel Trade Network is invite-only.
            <br />
            Ask an existing member for an invite link to join.
          </p>
        </div>
      </div>
    </div>
  );
}

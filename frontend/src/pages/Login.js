import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Shield, Eye, EyeSlash, ArrowRight, ShieldCheck } from '@phosphor-icons/react';

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

  // 2FA challenge state
  const [challengeToken, setChallengeToken] = useState('');
  const [code, setCode] = useState('');
  const [useRecovery, setUseRecovery] = useState(false);
  const [recoveryCode, setRecoveryCode] = useState('');

  const { login, loginVerify2FA } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const result = await login(email, password);
      if (result?.twoFactorRequired) {
        setChallengeToken(result.challengeToken);
      } else {
        navigate('/');
      }
    } catch (err) {
      if (err.response) {
        setError(formatApiErrorDetail(err.response.data?.detail) || 'Login failed. Please try again.');
      } else {
        setError("Couldn't reach the server. It may still be starting up after a deployment — please wait a moment and try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handle2FA = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await loginVerify2FA(
        challengeToken,
        useRecovery ? null : code,
        useRecovery ? recoveryCode : null
      );
      navigate('/');
    } catch (err) {
      if (err.response) {
        setError(formatApiErrorDetail(err.response.data?.detail) || 'Verification failed. Please try again.');
      } else {
        setError("Couldn't reach the server. It may still be starting up after a deployment — please wait a moment and try again.");
      }
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

          {error && (
            <div className="bg-[var(--brand-danger)]/20 border border-[var(--brand-danger)] text-[var(--text-primary)] px-4 py-3 mb-6" data-testid="login-error">
              {error}
            </div>
          )}

          {!challengeToken ? (
            <>
              <h2 className="text-xl font-semibold text-[var(--text-primary)] mb-6">Welcome Back</h2>
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
            </>
          ) : (
            <>
              <h2 className="text-xl font-semibold text-[var(--text-primary)] mb-2 flex items-center gap-2">
                <ShieldCheck size={22} className="text-[var(--brand-primary)]" />
                Two-Factor Authentication
              </h2>
              <p className="text-sm text-[var(--text-muted)] mb-6">
                {useRecovery
                  ? 'Enter one of your recovery codes.'
                  : 'Enter the 6-digit code from your authenticator app.'}
              </p>
              <form onSubmit={handle2FA} className="space-y-5">
                {useRecovery ? (
                  <input
                    type="text"
                    value={recoveryCode}
                    onChange={(e) => setRecoveryCode(e.target.value.toUpperCase())}
                    className="input-field w-full font-mono tracking-[0.2em] text-center"
                    placeholder="XXXXX-XXXXX"
                    autoFocus
                    required
                    data-testid="login-recovery-input"
                  />
                ) : (
                  <input
                    type="text"
                    inputMode="numeric"
                    pattern="[0-9]*"
                    maxLength={6}
                    value={code}
                    onChange={(e) => setCode(e.target.value.replace(/\D/g, ''))}
                    className="input-field w-full text-center text-xl tracking-[0.4em]"
                    placeholder="000000"
                    autoFocus
                    required
                    data-testid="login-2fa-input"
                  />
                )}
                <button
                  type="submit"
                  disabled={loading || (useRecovery ? !recoveryCode : code.length !== 6)}
                  className="btn-primary w-full"
                  data-testid="login-2fa-submit"
                >
                  {loading ? 'Verifying...' : 'Verify & Sign In'}
                </button>
                <div className="text-center">
                  <button
                    type="button"
                    onClick={() => { setUseRecovery(!useRecovery); setCode(''); setRecoveryCode(''); setError(''); }}
                    className="text-xs text-[var(--brand-primary)] hover:underline"
                    data-testid="toggle-recovery-button"
                  >
                    {useRecovery ? 'Use authenticator code instead' : "Lost your device? Use a recovery code"}
                  </button>
                </div>
                <div className="text-center">
                  <button
                    type="button"
                    onClick={() => { setChallengeToken(''); setCode(''); setRecoveryCode(''); setError(''); }}
                    className="text-xs text-[var(--text-muted)] hover:text-[var(--text-primary)]"
                    data-testid="cancel-2fa-button"
                  >
                    Cancel and start over
                  </button>
                </div>
              </form>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

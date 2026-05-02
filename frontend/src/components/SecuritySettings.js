import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { ShieldCheck, ShieldWarning, Key, Devices, X, Copy, Check } from '@phosphor-icons/react';
import { useAuth } from '../contexts/AuthContext';
import PasswordStrengthMeter from './PasswordStrengthMeter';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;
const ax = axios.create({ baseURL: API_URL, withCredentials: true });

function formatDetail(d) {
  if (d == null) return 'Something went wrong.';
  if (typeof d === 'string') return d;
  if (Array.isArray(d)) return d.map(e => e?.msg || JSON.stringify(e)).join(' ');
  return d?.msg || String(d);
}

function Enable2FAModal({ onClose, onEnabled }) {
  const [step, setStep] = useState('init'); // init, scan, codes
  const [qr, setQr] = useState('');
  const [secret, setSecret] = useState('');
  const [code, setCode] = useState('');
  const [recoveryCodes, setRecoveryCodes] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const res = await ax.post('/api/security/2fa/setup');
        setQr(res.data.qr_code);
        setSecret(res.data.secret);
        setStep('scan');
      } catch (e) {
        setError(formatDetail(e.response?.data?.detail) || e.message);
      }
    })();
  }, []);

  const confirm = async () => {
    setError(''); setLoading(true);
    try {
      const res = await ax.post('/api/security/2fa/confirm', { code });
      setRecoveryCodes(res.data.recovery_codes);
      setStep('codes');
    } catch (e) {
      setError(formatDetail(e.response?.data?.detail) || e.message);
    } finally {
      setLoading(false);
    }
  };

  const copyCodes = () => {
    navigator.clipboard.writeText(recoveryCodes.join('\n'));
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80" data-testid="enable-2fa-modal">
      <div className="bg-[var(--bg-surface)] border border-[var(--bg-surface-active)] w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-4 border-b border-[var(--bg-surface-active)]">
          <h3 className="text-lg font-semibold text-[var(--text-primary)] flex items-center gap-2">
            <ShieldCheck size={22} className="text-[var(--brand-primary)]" />
            Enable Two-Factor Authentication
          </h3>
          <button onClick={onClose} className="text-[var(--text-muted)] hover:text-[var(--text-primary)]" data-testid="close-2fa-modal">
            <X size={22} />
          </button>
        </div>

        {error && (
          <div className="m-4 bg-[var(--brand-danger)]/20 border border-[var(--brand-danger)] text-[var(--text-primary)] px-4 py-2 text-sm">
            {error}
          </div>
        )}

        {step === 'scan' && (
          <div className="p-6 space-y-4">
            <p className="text-sm text-[var(--text-secondary)]">
              Scan this QR code with an authenticator app (Google Authenticator, Authy, 1Password, etc.).
            </p>
            <div className="flex justify-center bg-white p-4">
              {qr && <img src={qr} alt="2FA QR Code" className="w-48 h-48" />}
            </div>
            <details className="text-xs text-[var(--text-muted)]">
              <summary className="cursor-pointer">Can't scan? Enter this key manually</summary>
              <code className="block mt-2 break-all bg-[var(--bg-surface-hover)] p-2 select-all">{secret}</code>
            </details>
            <div>
              <label className="block text-sm text-[var(--text-secondary)] mb-1">Enter the 6-digit code from your app</label>
              <input
                type="text"
                inputMode="numeric"
                pattern="[0-9]*"
                maxLength={6}
                value={code}
                onChange={(e) => setCode(e.target.value.replace(/\D/g, ''))}
                className="input-field w-full tracking-[0.4em] text-center text-lg"
                placeholder="000000"
                data-testid="2fa-confirm-code-input"
              />
            </div>
            <button
              onClick={confirm}
              disabled={loading || code.length !== 6}
              className="btn-primary w-full"
              data-testid="2fa-confirm-button"
            >
              {loading ? 'Verifying...' : 'Verify & Enable'}
            </button>
          </div>
        )}

        {step === 'codes' && (
          <div className="p-6 space-y-4">
            <div className="bg-[var(--brand-warning)]/15 border border-[var(--brand-warning)]/40 p-3 text-sm text-[var(--text-primary)]">
              <strong>Save these recovery codes</strong> in a safe place. Each code can be used once if you lose access to your authenticator.
            </div>
            <div className="grid grid-cols-2 gap-2 font-mono text-sm bg-[var(--bg-surface-hover)] p-4">
              {recoveryCodes.map((c) => (
                <span key={c} className="select-all" data-testid="recovery-code">{c}</span>
              ))}
            </div>
            <div className="flex gap-2">
              <button onClick={copyCodes} className="btn-secondary flex-1 flex items-center justify-center gap-2">
                {copied ? <Check size={18} /> : <Copy size={18} />}
                {copied ? 'Copied' : 'Copy All'}
              </button>
              <button onClick={onEnabled} className="btn-primary flex-1" data-testid="2fa-done-button">
                I've Saved Them
              </button>
            </div>
          </div>
        )}

        {step === 'init' && !error && (
          <div className="p-6 text-center text-[var(--text-muted)]">Preparing...</div>
        )}
      </div>
    </div>
  );
}

function Disable2FAModal({ onClose, onDisabled }) {
  const [password, setPassword] = useState('');
  const [code, setCode] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    setError(''); setLoading(true);
    try {
      await ax.post('/api/security/2fa/disable', { password, code });
      onDisabled();
    } catch (e) {
      setError(formatDetail(e.response?.data?.detail) || e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80" data-testid="disable-2fa-modal">
      <div className="bg-[var(--bg-surface)] border border-[var(--bg-surface-active)] w-full max-w-md">
        <div className="flex items-center justify-between p-4 border-b border-[var(--bg-surface-active)]">
          <h3 className="text-lg font-semibold text-[var(--text-primary)]">Disable Two-Factor</h3>
          <button onClick={onClose} className="text-[var(--text-muted)] hover:text-[var(--text-primary)]"><X size={22} /></button>
        </div>
        {error && <div className="m-4 bg-[var(--brand-danger)]/20 border border-[var(--brand-danger)] px-4 py-2 text-sm">{error}</div>}
        <div className="p-6 space-y-4">
          <input type="password" placeholder="Current password" value={password} onChange={(e) => setPassword(e.target.value)} className="input-field w-full" data-testid="disable-2fa-password" />
          <input type="text" inputMode="numeric" maxLength={6} placeholder="6-digit code" value={code} onChange={(e) => setCode(e.target.value.replace(/\D/g, ''))} className="input-field w-full tracking-[0.4em] text-center" data-testid="disable-2fa-code" />
          <button onClick={submit} disabled={loading} className="btn-primary w-full" data-testid="disable-2fa-submit">
            {loading ? 'Disabling...' : 'Disable 2FA'}
          </button>
        </div>
      </div>
    </div>
  );
}

function ChangePasswordSection() {
  const [current, setCurrent] = useState('');
  const [next, setNext] = useState('');
  const [confirm, setConfirm] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError('');
    if (next !== confirm) { setError('New passwords do not match.'); return; }
    setLoading(true);
    try {
      await ax.post('/api/security/password/change', { current_password: current, new_password: next });
      toast.success('Password changed. Other sessions signed out.');
      setCurrent(''); setNext(''); setConfirm('');
    } catch (e) {
      setError(formatDetail(e.response?.data?.detail) || e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={submit} className="space-y-3" data-testid="change-password-form">
      {error && <div className="bg-[var(--brand-danger)]/20 border border-[var(--brand-danger)] px-4 py-2 text-sm">{error}</div>}
      <input type="password" placeholder="Current password" value={current} onChange={(e) => setCurrent(e.target.value)} className="input-field w-full" required data-testid="current-password-input" />
      <input type="password" placeholder="New password" value={next} onChange={(e) => setNext(e.target.value)} className="input-field w-full" required data-testid="new-password-input" />
      <PasswordStrengthMeter password={next} />
      <input type="password" placeholder="Confirm new password" value={confirm} onChange={(e) => setConfirm(e.target.value)} className="input-field w-full" required data-testid="confirm-new-password-input" />
      <button type="submit" disabled={loading} className="btn-primary" data-testid="change-password-submit">
        {loading ? 'Updating...' : 'Update Password'}
      </button>
    </form>
  );
}

function SessionsList() {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      const res = await ax.get('/api/security/sessions');
      setSessions(res.data.sessions || []);
    } finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const revokeOne = async (sid) => {
    try {
      await ax.post('/api/security/sessions/revoke', { session_id: sid });
      toast.success('Session revoked.');
      load();
    } catch (e) {
      toast.error(formatDetail(e.response?.data?.detail));
    }
  };

  const revokeOthers = async () => {
    try {
      const res = await ax.post('/api/security/sessions/revoke-others');
      toast.success(res.data.message);
      load();
    } catch (e) {
      toast.error(formatDetail(e.response?.data?.detail));
    }
  };

  if (loading) return <p className="text-[var(--text-muted)] text-sm">Loading sessions...</p>;

  return (
    <div className="space-y-3" data-testid="sessions-list">
      {sessions.map((s) => (
        <div key={s.session_id} className="bg-[var(--bg-surface-hover)] border border-[var(--bg-surface-active)] p-3 flex items-start justify-between gap-3" data-testid="session-item">
          <div className="min-w-0">
            <p className="text-sm text-[var(--text-primary)] truncate">
              {s.user_agent || 'Unknown device'}
              {s.current && <span className="ml-2 text-xs px-2 py-0.5 bg-[var(--brand-primary)]/20 text-[var(--brand-primary)]">This device</span>}
            </p>
            <p className="text-xs text-[var(--text-muted)] mt-1">
              IP: {s.ip || '—'} · Last active: {s.last_used_at ? new Date(s.last_used_at).toLocaleString() : '—'}
            </p>
          </div>
          {!s.current && (
            <button
              onClick={() => revokeOne(s.session_id)}
              className="text-xs text-[var(--brand-danger)] hover:underline whitespace-nowrap"
              data-testid="revoke-session-button"
            >
              Sign out
            </button>
          )}
        </div>
      ))}
      {sessions.filter(s => !s.current).length > 0 && (
        <button onClick={revokeOthers} className="btn-secondary w-full" data-testid="revoke-others-button">
          Sign out of all other sessions
        </button>
      )}
    </div>
  );
}

export default function SecuritySettings() {
  const { user, checkAuth } = useAuth();
  const [showEnable, setShowEnable] = useState(false);
  const [showDisable, setShowDisable] = useState(false);
  const enabled = !!user?.two_factor_enabled;

  const refresh = async () => { await checkAuth(); };

  return (
    <div className="max-w-3xl mx-auto p-4 lg:p-8 space-y-8" data-testid="security-settings">
      <header>
        <h1 className="text-2xl font-bold text-[var(--text-primary)] flex items-center gap-2">
          <ShieldCheck size={28} weight="duotone" className="text-[var(--brand-primary)]" />
          Account Security
        </h1>
        <p className="text-sm text-[var(--text-muted)] mt-1">
          Strengthen your account with 2FA, manage active sessions, and rotate your password.
        </p>
      </header>

      {/* 2FA */}
      <section className="bg-[var(--bg-surface)] border border-[var(--bg-surface-active)] p-6">
        <div className="flex items-start justify-between gap-4 mb-3">
          <div>
            <h2 className="text-lg font-semibold text-[var(--text-primary)] flex items-center gap-2">
              {enabled
                ? <ShieldCheck size={22} className="text-[var(--brand-success)]" />
                : <ShieldWarning size={22} className="text-[var(--brand-warning)]" />}
              Two-Factor Authentication
            </h2>
            <p className="text-sm text-[var(--text-muted)] mt-1">
              {enabled
                ? 'Your account is protected with an authenticator app.'
                : 'Require a 6-digit code from your authenticator app at sign-in. Strongly recommended for verified traders and admins.'}
            </p>
          </div>
          {enabled ? (
            <button onClick={() => setShowDisable(true)} className="btn-secondary whitespace-nowrap" data-testid="disable-2fa-button">
              Disable
            </button>
          ) : (
            <button onClick={() => setShowEnable(true)} className="btn-primary whitespace-nowrap" data-testid="enable-2fa-button">
              Enable 2FA
            </button>
          )}
        </div>
      </section>

      {/* Password */}
      <section className="bg-[var(--bg-surface)] border border-[var(--bg-surface-active)] p-6">
        <h2 className="text-lg font-semibold text-[var(--text-primary)] flex items-center gap-2 mb-4">
          <Key size={22} className="text-[var(--brand-primary)]" />
          Change Password
        </h2>
        <ChangePasswordSection />
      </section>

      {/* Sessions */}
      <section className="bg-[var(--bg-surface)] border border-[var(--bg-surface-active)] p-6">
        <h2 className="text-lg font-semibold text-[var(--text-primary)] flex items-center gap-2 mb-4">
          <Devices size={22} className="text-[var(--brand-primary)]" />
          Active Sessions
        </h2>
        <SessionsList />
      </section>

      {showEnable && (
        <Enable2FAModal
          onClose={() => setShowEnable(false)}
          onEnabled={async () => { setShowEnable(false); await refresh(); toast.success('2FA enabled.'); }}
        />
      )}
      {showDisable && (
        <Disable2FAModal
          onClose={() => setShowDisable(false)}
          onDisabled={async () => { setShowDisable(false); await refresh(); toast.success('2FA disabled.'); }}
        />
      )}
    </div>
  );
}

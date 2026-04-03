import { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Shield, Eye, EyeSlash, ArrowRight, MapPin, WarningCircle, FileText, CheckSquare, Square } from '@phosphor-icons/react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;

function formatApiErrorDetail(detail) {
  if (detail == null) return "Something went wrong. Please try again.";
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail))
    return detail.map((e) => (e && typeof e.msg === "string" ? e.msg : JSON.stringify(e))).filter(Boolean).join(" ");
  if (detail && typeof detail.msg === "string") return detail.msg;
  return String(detail);
}

function InviteGate() {
  return (
    <div className="min-h-screen flex items-center justify-center relative"
         style={{ 
           backgroundImage: 'url(https://images.unsplash.com/photo-1604549001484-df28edea610b?crop=entropy&cs=srgb&fm=jpg&q=85)',
           backgroundSize: 'cover',
           backgroundPosition: 'center'
         }}>
      <div className="absolute inset-0 bg-black/70"></div>
      <div className="relative z-10 w-full max-w-md p-8 animate-fade-in">
        <div className="bg-[var(--bg-surface)] border border-[var(--bg-surface-active)] border-t-[3px] border-t-[var(--brand-danger)] p-8 text-center" data-testid="invite-gate">
          <WarningCircle size={48} weight="duotone" className="text-[var(--brand-danger)] mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-[var(--text-primary)] mb-3">Invite Required</h2>
          <p className="text-[var(--text-secondary)] mb-6">
            Rebel Trade Network is invite-only. You need a valid invitation link from an existing member to join.
          </p>
          <p className="text-[var(--text-muted)] text-sm mb-6">
            Know someone in the network? Ask them to send you an invite link.
          </p>
          <Link to="/login" className="btn-primary inline-flex items-center gap-2" data-testid="back-to-login-link">
            Already a member? Sign In
          </Link>
        </div>
      </div>
    </div>
  );
}

export default function Register() {
  const [searchParams] = useSearchParams();
  const inviteToken = searchParams.get('invite');
  
  const [inviteValid, setInviteValid] = useState(null); // null=loading, true=valid, false=invalid
  const [invitedBy, setInvitedBy] = useState('');
  const [inviteError, setInviteError] = useState('');
  
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [location, setLocation] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [acceptedTerms, setAcceptedTerms] = useState(false);
  const [showTermsModal, setShowTermsModal] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const validateInvite = useCallback(async () => {
    try {
      const res = await axios.get(`${API_URL}/api/invites/validate/${inviteToken}`);
      setInviteValid(true);
      setInvitedBy(res.data.invited_by || '');
    } catch (err) {
      setInviteValid(false);
      setInviteError(
        err.response?.status === 410
          ? 'This invite link has expired. Please request a new one.'
          : 'This invite link is invalid or has already been used.'
      );
    }
  }, [inviteToken]);

  useEffect(() => {
    if (!inviteToken) {
      setInviteValid(false);
      return;
    }
    validateInvite();
  }, [inviteToken, validateInvite]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!acceptedTerms) {
      setError('You must accept the Community Guidelines & Terms to join');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setLoading(true);

    try {
      await register(email, password, name, location, inviteToken);
      navigate('/');
    } catch (err) {
      setError(formatApiErrorDetail(err.response?.data?.detail) || err.message);
    } finally {
      setLoading(false);
    }
  };

  // No invite token or invalid token — show gate
  if (inviteValid === null) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[var(--bg-main)]">
        <div className="text-[var(--text-secondary)]">Validating invite...</div>
      </div>
    );
  }

  if (inviteValid === false) {
    if (inviteError) {
      return (
        <div className="min-h-screen flex items-center justify-center relative"
             style={{ 
               backgroundImage: 'url(https://images.unsplash.com/photo-1604549001484-df28edea610b?crop=entropy&cs=srgb&fm=jpg&q=85)',
               backgroundSize: 'cover',
               backgroundPosition: 'center'
             }}>
          <div className="absolute inset-0 bg-black/70"></div>
          <div className="relative z-10 w-full max-w-md p-8 animate-fade-in">
            <div className="bg-[var(--bg-surface)] border border-[var(--bg-surface-active)] border-t-[3px] border-t-[var(--brand-danger)] p-8 text-center" data-testid="invite-expired">
              <WarningCircle size={48} weight="duotone" className="text-[var(--brand-danger)] mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-[var(--text-primary)] mb-3">Invalid Invite</h2>
              <p className="text-[var(--text-secondary)] mb-6">{inviteError}</p>
              <Link to="/login" className="btn-primary inline-flex items-center gap-2" data-testid="back-to-login-link">
                Back to Sign In
              </Link>
            </div>
          </div>
        </div>
      );
    }
    return <InviteGate />;
  }

  return (
    <div className="min-h-screen flex items-center justify-center relative py-8" 
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

          {invitedBy && (
            <div className="bg-[var(--brand-primary)]/10 border border-[var(--brand-primary)]/30 text-[var(--text-primary)] px-4 py-3 mb-6 text-sm" data-testid="invite-info">
              You've been invited by <span className="font-semibold text-[var(--brand-primary)]">{invitedBy}</span>
            </div>
          )}

          <h2 className="text-xl font-semibold text-[var(--text-primary)] mb-6">Join the Network</h2>

          {error && (
            <div className="bg-[var(--brand-danger)]/20 border border-[var(--brand-danger)] text-[var(--text-primary)] px-4 py-3 mb-6" data-testid="register-error">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm text-[var(--text-secondary)] mb-2">Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="input-field w-full"
                placeholder="Your name"
                required
                data-testid="register-name-input"
              />
            </div>

            <div>
              <label className="block text-sm text-[var(--text-secondary)] mb-2">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input-field w-full"
                placeholder="you@homestead.com"
                required
                data-testid="register-email-input"
              />
            </div>

            <div>
              <label className="block text-sm text-[var(--text-secondary)] mb-2">
                <MapPin size={16} className="inline mr-1" />
                Location (Region/Area)
              </label>
              <input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className="input-field w-full"
                placeholder="e.g., Pacific Northwest, Rural Texas"
                data-testid="register-location-input"
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
                  placeholder="Create a password"
                  required
                  data-testid="register-password-input"
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

            <div>
              <label className="block text-sm text-[var(--text-secondary)] mb-2">Confirm Password</label>
              <input
                type={showPassword ? 'text' : 'password'}
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="input-field w-full"
                placeholder="Confirm your password"
                required
                data-testid="register-confirm-password-input"
              />
            </div>

            {/* Community Guidelines & Terms Acceptance */}
            <div className="bg-[var(--bg-surface-hover)] border border-[var(--bg-surface-active)] p-4 mt-4">
              <div className="flex items-start gap-3">
                <button
                  type="button"
                  onClick={() => setAcceptedTerms(!acceptedTerms)}
                  className="mt-0.5 text-[var(--brand-primary)] hover:text-[var(--brand-primary-hover)] transition-colors flex-shrink-0"
                  data-testid="terms-checkbox"
                >
                  {acceptedTerms ? (
                    <CheckSquare size={24} weight="fill" />
                  ) : (
                    <Square size={24} weight="regular" />
                  )}
                </button>
                <div className="text-sm">
                  <p className="text-[var(--text-primary)] mb-2">
                    I have read and agree to the{' '}
                    <button
                      type="button"
                      onClick={() => setShowTermsModal(true)}
                      className="text-[var(--brand-primary)] hover:text-[var(--brand-primary-hover)] underline inline-flex items-center gap-1"
                      data-testid="view-terms-button"
                    >
                      <FileText size={14} />
                      Community Guidelines & Terms
                    </button>
                  </p>
                  <p className="text-[var(--text-muted)] text-xs leading-relaxed">
                    By joining, I acknowledge that I am solely responsible for all trade deals I make on this platform, and the creators of Rebel Trade Network are not liable for any transactions.
                  </p>
                </div>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading || !acceptedTerms}
              className={`btn-primary w-full flex items-center justify-center gap-2 mt-6 ${!acceptedTerms ? 'opacity-50 cursor-not-allowed' : ''}`}
              data-testid="register-submit-button"
            >
              {loading ? 'Creating Account...' : (
                <>
                  Join the Network
                  <ArrowRight size={20} weight="bold" />
                </>
              )}
            </button>
          </form>

          <p className="mt-6 text-center text-[var(--text-muted)]">
            Already a member?{' '}
            <Link to="/login" className="text-[var(--brand-primary)] hover:text-[var(--brand-primary-hover)]" data-testid="login-link">
              Sign In
            </Link>
          </p>
        </div>
      </div>

      {/* Terms Modal */}
      {showTermsModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80" data-testid="terms-modal">
          <div className="bg-[var(--bg-surface)] border border-[var(--bg-surface-active)] w-full max-w-2xl max-h-[80vh] overflow-hidden flex flex-col animate-fade-in">
            <div className="flex items-center justify-between p-4 border-b border-[var(--bg-surface-active)]">
              <div className="flex items-center gap-2">
                <FileText size={24} className="text-[var(--brand-primary)]" />
                <h3 className="text-lg font-semibold text-[var(--text-primary)]">Community Guidelines & Terms</h3>
              </div>
              <button
                onClick={() => setShowTermsModal(false)}
                className="text-[var(--text-muted)] hover:text-[var(--text-primary)] text-2xl leading-none"
                data-testid="close-terms-modal"
              >
                ×
              </button>
            </div>
            
            <div className="p-6 overflow-y-auto flex-1 space-y-6 text-[var(--text-secondary)]">
              {/* Prohibited Activities */}
              <section>
                <h4 className="text-[var(--text-primary)] font-semibold mb-3 flex items-center gap-2">
                  <WarningCircle size={20} className="text-[var(--brand-danger)]" />
                  Prohibited Activities
                </h4>
                <ul className="space-y-2 text-sm list-disc list-inside">
                  <li><span className="text-[var(--brand-danger)] font-semibold">User is responsible for following all applicable laws.</span> You are solely responsible for ensuring that any items you trade, sell, or exchange comply with all local, state, and federal laws. This includes but is not limited to controlled substances, regulated goods, and any items prohibited in your jurisdiction.</li>
                  <li><span className="text-[var(--brand-danger)] font-semibold">No weapons trafficking.</span> Trading of firearms, explosives, or other regulated weapons must comply with all applicable laws and regulations.</li>
                  <li><span className="text-[var(--brand-danger)] font-semibold">No counterfeit goods.</span> Fake, fraudulent, or misrepresented items are not allowed.</li>
                </ul>
              </section>

              {/* Community Standards */}
              <section>
                <h4 className="text-[var(--text-primary)] font-semibold mb-3 flex items-center gap-2">
                  <Shield size={20} className="text-[var(--brand-primary)]" />
                  Community Standards
                </h4>
                <ul className="space-y-2 text-sm list-disc list-inside">
                  <li><span className="text-[var(--brand-primary)] font-semibold">No harassment.</span> Bullying, intimidation, stalking, or any form of harassment towards other members will not be tolerated.</li>
                  <li><span className="text-[var(--brand-primary)] font-semibold">No threats or violence.</span> Any threats of violence, promotion of violence, or incitement to harm others is strictly prohibited and may be reported to authorities.</li>
                  <li><span className="text-[var(--brand-primary)] font-semibold">No hate speech.</span> Discrimination, slurs, or hateful content targeting individuals or groups is not allowed.</li>
                  <li><span className="text-[var(--brand-primary)] font-semibold">Respect privacy.</span> Do not share other members' personal information without consent.</li>
                </ul>
              </section>

              {/* Liability Disclaimer */}
              <section className="bg-[var(--bg-surface-hover)] border border-[var(--bg-surface-active)] p-4">
                <h4 className="text-[var(--text-primary)] font-semibold mb-3">Liability Disclaimer</h4>
                <div className="text-sm space-y-3">
                  <p>
                    <strong className="text-[var(--text-primary)]">User Responsibility:</strong> You are solely responsible for any and all trade deals, transactions, communications, and interactions you engage in through Rebel Trade Network. This includes verifying the legitimacy of items, the trustworthiness of trading partners, and ensuring compliance with all applicable laws.
                  </p>
                  <p>
                    <strong className="text-[var(--text-primary)]">No Liability:</strong> The creators, operators, and administrators of Rebel Trade Network are NOT liable for any losses, damages, disputes, injuries, or legal consequences arising from trades, transactions, or interactions made through this platform.
                  </p>
                  <p>
                    <strong className="text-[var(--text-primary)]">Trade at Your Own Risk:</strong> All trades are conducted at your own risk. We do not guarantee, verify, or endorse any items, services, or members on this platform.
                  </p>
                </div>
              </section>

              {/* Enforcement */}
              <section>
                <h4 className="text-[var(--text-primary)] font-semibold mb-3">Enforcement</h4>
                <p className="text-sm">
                  Violations of these guidelines may result in warnings, suspension, or permanent removal from the network. Severe violations may be reported to appropriate law enforcement agencies.
                </p>
              </section>
            </div>

            <div className="p-4 border-t border-[var(--bg-surface-active)] flex gap-3">
              <button
                onClick={() => setShowTermsModal(false)}
                className="flex-1 py-2 px-4 border border-[var(--bg-surface-active)] text-[var(--text-secondary)] hover:bg-[var(--bg-surface-hover)] transition-colors"
                data-testid="terms-close-button"
              >
                Close
              </button>
              <button
                onClick={() => {
                  setAcceptedTerms(true);
                  setShowTermsModal(false);
                }}
                className="flex-1 btn-primary"
                data-testid="terms-accept-button"
              >
                I Accept
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Shield, Eye, EyeSlash, ArrowRight, MapPin } from '@phosphor-icons/react';

function formatApiErrorDetail(detail) {
  if (detail == null) return "Something went wrong. Please try again.";
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail))
    return detail.map((e) => (e && typeof e.msg === "string" ? e.msg : JSON.stringify(e))).filter(Boolean).join(" ");
  if (detail && typeof detail.msg === "string") return detail.msg;
  return String(detail);
}

export default function Register() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [location, setLocation] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

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
      await register(email, password, name, location);
      navigate('/');
    } catch (err) {
      setError(formatApiErrorDetail(err.response?.data?.detail) || err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center relative py-8" 
         style={{ 
           backgroundImage: 'url(https://images.unsplash.com/photo-1604549001484-df28edea610b?crop=entropy&cs=srgb&fm=jpg&q=85)',
           backgroundSize: 'cover',
           backgroundPosition: 'center'
         }}>
      <div className="absolute inset-0 bg-black/70"></div>
      
      <div className="relative z-10 w-full max-w-md p-8 animate-fade-in">
        <div className="bg-[#1C1917] border border-[#292524] p-8">
          <div className="flex items-center gap-3 mb-8">
            <Shield size={40} weight="duotone" className="text-[#B45309]" />
            <div>
              <h1 className="text-2xl font-black tracking-tight text-[#E7E5E4]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
                HOMESTEAD HUB
              </h1>
              <p className="text-xs uppercase tracking-[0.2em] text-[#78716C]">Exit the Matrix</p>
            </div>
          </div>

          <h2 className="text-xl font-semibold text-[#E7E5E4] mb-6">Join the Network</h2>

          {error && (
            <div className="bg-[#991B1B]/20 border border-[#991B1B] text-[#E7E5E4] px-4 py-3 mb-6" data-testid="register-error">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm text-[#A8A29E] mb-2">Name</label>
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
              <label className="block text-sm text-[#A8A29E] mb-2">Email</label>
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
              <label className="block text-sm text-[#A8A29E] mb-2">
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
              <label className="block text-sm text-[#A8A29E] mb-2">Password</label>
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
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-[#78716C] hover:text-[#E7E5E4]"
                >
                  {showPassword ? <EyeSlash size={20} /> : <Eye size={20} />}
                </button>
              </div>
            </div>

            <div>
              <label className="block text-sm text-[#A8A29E] mb-2">Confirm Password</label>
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

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full flex items-center justify-center gap-2 mt-6"
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

          <p className="mt-6 text-center text-[#78716C]">
            Already a member?{' '}
            <Link to="/login" className="text-[#B45309] hover:text-[#92400E]" data-testid="login-link">
              Sign In
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

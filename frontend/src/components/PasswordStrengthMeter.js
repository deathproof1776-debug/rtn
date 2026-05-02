import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const LABELS = ['Very Weak', 'Weak', 'Fair', 'Strong', 'Excellent'];
const COLORS = ['#dc2626', '#ea580c', '#ca8a04', '#65a30d', '#16a34a'];

export default function PasswordStrengthMeter({ password, userInputs = [] }) {
  const [score, setScore] = useState(0);
  const [warning, setWarning] = useState('');
  const [suggestions, setSuggestions] = useState([]);

  const check = useCallback(async () => {
    if (!password) {
      setScore(0); setWarning(''); setSuggestions([]);
      return;
    }
    try {
      const res = await axios.post(`${API_URL}/api/auth/password/check`,
        { password, user_inputs: userInputs });
      setScore(res.data.score || 0);
      setWarning(res.data.warning || '');
      setSuggestions(res.data.suggestions || []);
    } catch {
      // ignore
    }
  }, [password, userInputs]);

  useEffect(() => {
    const t = setTimeout(check, 250);
    return () => clearTimeout(t);
  }, [check]);

  if (!password) return null;

  return (
    <div className="mt-2" data-testid="password-strength-meter">
      <div className="flex gap-1 mb-1">
        {[0, 1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="h-1 flex-1 rounded transition-colors"
            style={{ background: i <= score ? COLORS[score] : 'var(--bg-surface-active)' }}
          />
        ))}
      </div>
      <div className="flex items-center justify-between text-xs">
        <span style={{ color: COLORS[score] }} data-testid="password-strength-label">
          {LABELS[score]}
        </span>
        {score < 2 && (
          <span className="text-[var(--brand-danger)] text-xs">Minimum: Fair</span>
        )}
      </div>
      {warning && (
        <p className="text-xs text-[var(--text-muted)] mt-1">{warning}</p>
      )}
      {suggestions.length > 0 && score < 3 && (
        <p className="text-xs text-[var(--text-muted)] mt-1">{suggestions.join(' ')}</p>
      )}
    </div>
  );
}

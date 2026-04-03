/**
 * SystemBanner - Scrolling marquee for admin announcements
 */
import { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Info, 
  Warning, 
  CheckCircle, 
  Megaphone,
  X
} from '@phosphor-icons/react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function SystemBanner() {
  const [messages, setMessages] = useState([]);
  const [dismissed, setDismissed] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMessages();
  }, []);

  const fetchMessages = async () => {
    try {
      const res = await axios.get(`${API_URL}/api/admin/system-messages/active`);
      setMessages(res.data.messages || []);
    } catch (error) {
      console.error('Error fetching system messages:', error);
    } finally {
      setLoading(false);
    }
  };

  const dismissMessage = (messageId) => {
    setDismissed([...dismissed, messageId]);
  };

  const getIcon = (type) => {
    switch (type) {
      case 'warning':
        return <Warning size={16} weight="fill" />;
      case 'success':
        return <CheckCircle size={16} weight="fill" />;
      case 'urgent':
        return <Megaphone size={16} weight="fill" />;
      default:
        return <Info size={16} weight="fill" />;
    }
  };

  const getTypeStyles = (type) => {
    switch (type) {
      case 'warning':
        return 'bg-yellow-900/80 border-yellow-600 text-yellow-200';
      case 'success':
        return 'bg-green-900/80 border-green-600 text-green-200';
      case 'urgent':
        return 'bg-red-900/80 border-red-600 text-red-200';
      default:
        return 'bg-[var(--brand-primary)]/20 border-[var(--brand-primary)] text-[var(--brand-primary)]';
    }
  };

  const visibleMessages = messages.filter(m => !dismissed.includes(m._id));

  if (loading || visibleMessages.length === 0) {
    return null;
  }

  return (
    <div className="mb-4" data-testid="system-banner">
      {visibleMessages.map((msg) => (
        <div
          key={msg._id}
          className={`relative overflow-hidden border-l-4 rounded mb-2 ${getTypeStyles(msg.type)}`}
          data-testid={`system-message-${msg._id}`}
        >
          <div className="flex items-center px-3 py-2">
            <span className="flex-shrink-0 mr-2">
              {getIcon(msg.type)}
            </span>
            
            {/* Scrolling text for long messages */}
            <div className="flex-1 overflow-hidden">
              {msg.message.length > 80 ? (
                <div className="animate-marquee whitespace-nowrap">
                  <span className="mr-8">{msg.message}</span>
                  <span className="mr-8">{msg.message}</span>
                </div>
              ) : (
                <span className="text-sm">{msg.message}</span>
              )}
            </div>
            
            <button
              onClick={() => dismissMessage(msg._id)}
              className="flex-shrink-0 ml-2 p-1 hover:bg-white/10 rounded transition-colors"
              aria-label="Dismiss"
              data-testid={`dismiss-message-${msg._id}`}
            >
              <X size={14} />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}

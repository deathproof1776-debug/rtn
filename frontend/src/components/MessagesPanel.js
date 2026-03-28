import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { 
  PaperPlaneRight, 
  ChatCircle, 
  ArrowLeft,
  Circle
} from '@phosphor-icons/react';
import { formatDistanceToNow } from 'date-fns';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function MessagesPanel() {
  const { user } = useAuth();
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    fetchConversations();
  }, []);

  useEffect(() => {
    if (selectedConversation) {
      fetchMessages(selectedConversation.user_id);
    }
  }, [selectedConversation]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchConversations = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/conversations`, {
        withCredentials: true
      });
      setConversations(response.data);
    } catch (error) {
      console.error('Error fetching conversations:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchMessages = async (userId) => {
    try {
      const response = await axios.get(`${API_URL}/api/messages/${userId}`, {
        withCredentials: true
      });
      setMessages(response.data);
    } catch (error) {
      console.error('Error fetching messages:', error);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !selectedConversation) return;

    setSending(true);
    try {
      await axios.post(`${API_URL}/api/messages`, {
        receiver_id: selectedConversation.user_id,
        content: newMessage
      }, { withCredentials: true });

      setMessages([...messages, {
        id: Date.now().toString(),
        sender_id: user.id,
        receiver_id: selectedConversation.user_id,
        content: newMessage,
        created_at: new Date().toISOString(),
        read: false
      }]);
      setNewMessage('');
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setSending(false);
    }
  };

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-[#78716C]">Loading conversations...</div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col" data-testid="messages-panel">
      <div className="flex items-center gap-2 mb-4 md:mb-6">
        <ChatCircle size={22} weight="duotone" className="text-[#B45309]" />
        <h2 className="text-xl md:text-2xl font-bold text-[#E7E5E4]" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
          Messages
        </h2>
      </div>

      {selectedConversation ? (
        <div className="flex-1 flex flex-col bg-[#1C1917] border border-[#292524] -mx-4 md:mx-0">
          <div className="flex items-center gap-2 md:gap-3 p-3 md:p-4 border-b border-[#292524]">
            <button 
              onClick={() => setSelectedConversation(null)}
              className="btn-ghost p-1.5 md:p-2"
              data-testid="back-to-conversations"
            >
              <ArrowLeft size={20} />
            </button>
            <div className="w-9 h-9 md:w-10 md:h-10 bg-[#292524] flex items-center justify-center text-[#B45309] font-semibold text-sm md:text-base flex-shrink-0">
              {selectedConversation.user_name?.charAt(0)?.toUpperCase() || 'U'}
            </div>
            <div className="min-w-0">
              <h3 className="font-medium text-[#E7E5E4] text-sm md:text-base truncate">{selectedConversation.user_name}</h3>
              <p className="text-[10px] md:text-xs text-[#78716C]">Encrypted</p>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-3 md:p-4 space-y-3 md:space-y-4">
            {messages.length === 0 ? (
              <div className="text-center text-[#78716C] py-8 text-sm">
                Start the conversation by sending a message
              </div>
            ) : (
              messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`message-bubble ${msg.sender_id === user.id ? 'message-sent' : 'message-received'}`}
                  data-testid={`message-${msg.id}`}
                >
                  <p className="text-sm">{msg.content}</p>
                  <p className="text-[10px] md:text-xs opacity-60 mt-1">
                    {msg.created_at ? formatDistanceToNow(new Date(msg.created_at), { addSuffix: true }) : ''}
                  </p>
                </div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={sendMessage} className="p-3 md:p-4 border-t border-[#292524]">
            <div className="flex gap-2">
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="Type your message..."
                className="input-field flex-1"
                data-testid="message-input"
              />
              <button 
                type="submit" 
                disabled={sending || !newMessage.trim()}
                className="btn-primary px-3 md:px-4"
                data-testid="send-message-button"
              >
                <PaperPlaneRight size={18} weight="fill" />
              </button>
            </div>
          </form>
        </div>
      ) : (
        <div className="space-y-2">
          {conversations.length === 0 ? (
            <div className="bg-[#1C1917] border border-[#292524] p-6 md:p-8 text-center">
              <ChatCircle size={40} className="mx-auto text-[#44403C] mb-3 md:mb-4" />
              <h3 className="text-base md:text-lg font-semibold text-[#E7E5E4] mb-2">No conversations yet</h3>
              <p className="text-xs md:text-sm text-[#78716C]">
                Start a conversation by reaching out to other homesteaders
              </p>
            </div>
          ) : (
            conversations.map((conv) => (
              <button
                key={conv.user_id}
                onClick={() => setSelectedConversation(conv)}
                className="w-full bg-[#1C1917] border border-[#292524] p-3 md:p-4 text-left card-hover"
                data-testid={`conversation-${conv.user_id}`}
              >
                <div className="flex items-center gap-2.5 md:gap-3">
                  <div className="relative flex-shrink-0">
                    <div className="w-11 h-11 md:w-12 md:h-12 bg-[#292524] flex items-center justify-center text-[#B45309] font-semibold text-sm md:text-base">
                      {conv.user_name?.charAt(0)?.toUpperCase() || 'U'}
                    </div>
                    {conv.unread_count > 0 && (
                      <div className="absolute -top-1 -right-1 w-4 h-4 md:w-5 md:h-5 bg-[#B45309] flex items-center justify-center text-[10px] md:text-xs">
                        {conv.unread_count}
                      </div>
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-2">
                      <h4 className="font-medium text-[#E7E5E4] text-sm md:text-base truncate">{conv.user_name}</h4>
                      <span className="text-[10px] md:text-xs text-[#78716C] flex-shrink-0">
                        {conv.last_message_at ? formatDistanceToNow(new Date(conv.last_message_at), { addSuffix: true }) : ''}
                      </span>
                    </div>
                    <p className="text-xs md:text-sm text-[#78716C] truncate">{conv.last_message}</p>
                  </div>
                </div>
              </button>
            ))
          )}
        </div>
      )}
    </div>
  );
}

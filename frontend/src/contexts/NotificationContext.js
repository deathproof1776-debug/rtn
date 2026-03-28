import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useAuth } from './AuthContext';
import axios from 'axios';

const NotificationContext = createContext(null);

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Convert base64 string to Uint8Array for push subscription
function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding)
    .replace(/-/g, '+')
    .replace(/_/g, '/');

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

export function NotificationProvider({ children }) {
  const { user } = useAuth();
  const [permission, setPermission] = useState('default');
  const [subscription, setSubscription] = useState(null);
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [loading, setLoading] = useState(false);
  const [swRegistration, setSwRegistration] = useState(null);

  // Check if push notifications are supported
  const isSupported = 'serviceWorker' in navigator && 'PushManager' in window && 'Notification' in window;

  // Initialize service worker
  useEffect(() => {
    if (!isSupported) {
      console.log('Push notifications not supported');
      return;
    }

    // Register service worker
    navigator.serviceWorker.register('/sw.js')
      .then((registration) => {
        console.log('Service Worker registered:', registration.scope);
        setSwRegistration(registration);
        
        // Check current permission
        setPermission(Notification.permission);
        
        // Check if already subscribed
        registration.pushManager.getSubscription()
          .then((sub) => {
            if (sub) {
              setSubscription(sub);
              setIsSubscribed(true);
            }
          });
      })
      .catch((error) => {
        console.error('Service Worker registration failed:', error);
      });
  }, [isSupported]);

  // Subscribe to push notifications
  const subscribe = useCallback(async () => {
    if (!isSupported || !swRegistration || !user) {
      return { success: false, error: 'Not supported or not logged in' };
    }

    setLoading(true);

    try {
      // Request notification permission
      const perm = await Notification.requestPermission();
      setPermission(perm);

      if (perm !== 'granted') {
        setLoading(false);
        return { success: false, error: 'Permission denied' };
      }

      // Get VAPID public key from backend
      const keyResponse = await axios.get(`${API_URL}/api/notifications/vapid-public-key`, {
        withCredentials: true
      });
      const vapidPublicKey = keyResponse.data.publicKey;

      if (!vapidPublicKey) {
        setLoading(false);
        return { success: false, error: 'VAPID key not configured' };
      }

      // Subscribe to push manager
      const sub = await swRegistration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(vapidPublicKey)
      });

      // Send subscription to backend
      const subJson = sub.toJSON();
      await axios.post(`${API_URL}/api/notifications/subscribe`, {
        endpoint: subJson.endpoint,
        keys: {
          p256dh: subJson.keys.p256dh,
          auth: subJson.keys.auth
        }
      }, { withCredentials: true });

      setSubscription(sub);
      setIsSubscribed(true);
      setLoading(false);

      return { success: true };
    } catch (error) {
      console.error('Push subscription failed:', error);
      setLoading(false);
      return { success: false, error: error.message };
    }
  }, [isSupported, swRegistration, user]);

  // Unsubscribe from push notifications
  const unsubscribe = useCallback(async () => {
    if (!subscription) {
      return { success: false, error: 'Not subscribed' };
    }

    setLoading(true);

    try {
      // Get subscription info before unsubscribing
      const subJson = subscription.toJSON();

      // Unsubscribe from push manager
      await subscription.unsubscribe();

      // Notify backend
      await axios.post(`${API_URL}/api/notifications/unsubscribe`, {
        endpoint: subJson.endpoint,
        keys: {
          p256dh: subJson.keys.p256dh,
          auth: subJson.keys.auth
        }
      }, { withCredentials: true });

      setSubscription(null);
      setIsSubscribed(false);
      setLoading(false);

      return { success: true };
    } catch (error) {
      console.error('Push unsubscription failed:', error);
      setLoading(false);
      return { success: false, error: error.message };
    }
  }, [subscription]);

  // Send test notification
  const sendTestNotification = useCallback(async () => {
    if (!isSubscribed) {
      return { success: false, error: 'Not subscribed' };
    }

    try {
      await axios.post(`${API_URL}/api/notifications/test`, {}, { withCredentials: true });
      return { success: true };
    } catch (error) {
      console.error('Test notification failed:', error);
      return { success: false, error: error.message };
    }
  }, [isSubscribed]);

  return (
    <NotificationContext.Provider value={{
      isSupported,
      permission,
      isSubscribed,
      loading,
      subscribe,
      unsubscribe,
      sendTestNotification
    }}>
      {children}
    </NotificationContext.Provider>
  );
}

export function useNotifications() {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
}

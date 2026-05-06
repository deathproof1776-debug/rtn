import { createContext, useContext, useState, useEffect, useCallback, useMemo } from 'react';
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

  // Initialize service worker (uses the registration from index.js — does not double-register)
  useEffect(() => {
    if (!isSupported) {
      console.log('Push notifications not supported');
      return;
    }

    let cancelled = false;

    // Wait for any existing/active SW registration (registered by index.js).
    // navigator.serviceWorker.ready resolves once a SW is fully activated.
    navigator.serviceWorker.ready
      .then((registration) => {
        if (cancelled) return;
        console.log('Service Worker ready:', registration.scope);
        setSwRegistration(registration);
        setPermission(Notification.permission);

        return registration.pushManager.getSubscription();
      })
      .then((sub) => {
        if (cancelled) return;
        if (sub) {
          setSubscription(sub);
          setIsSubscribed(true);
        }
      })
      .catch((error) => {
        console.error('Service Worker not ready:', error);
      });

    // Listen for permission changes (user updates browser settings)
    let permStatus;
    if (navigator.permissions?.query) {
      navigator.permissions.query({ name: 'notifications' }).then((status) => {
        if (cancelled) return;
        permStatus = status;
        setPermission(status.state === 'prompt' ? 'default' : status.state);
        const onChange = () => setPermission(status.state === 'prompt' ? 'default' : status.state);
        status.addEventListener('change', onChange);
        permStatus._cleanup = () => status.removeEventListener('change', onChange);
      }).catch(() => {});
    }

    return () => {
      cancelled = true;
      if (permStatus?._cleanup) permStatus._cleanup();
    };
  }, [isSupported]);

  // Subscribe to push notifications
  const subscribe = useCallback(async () => {
    if (!isSupported) {
      console.error('[Notifications] Push notifications not supported in this browser');
      return { success: false, error: 'Push notifications not supported in this browser' };
    }

    if (!user) {
      console.error('[Notifications] User not logged in');
      return { success: false, error: 'Please log in first' };
    }

    setLoading(true);
    console.log('[Notifications] Starting subscription process...');

    try {
      // Request notification permission FIRST (must be in user-gesture call stack)
      console.log('[Notifications] Requesting permission...');
      const perm = await Notification.requestPermission();
      console.log('[Notifications] Permission result:', perm);
      setPermission(perm);

      if (perm !== 'granted') {
        setLoading(false);
        return {
          success: false,
          error: perm === 'denied'
            ? 'You blocked notifications for this site. Open your browser site settings and allow notifications, then try again.'
            : 'Permission was not granted'
        };
      }

      // Ensure SW is fully ready (covers cold start where registration is still activating)
      let registration = swRegistration;
      if (!registration || !registration.active) {
        console.log('[Notifications] Waiting for SW to be ready...');
        registration = await navigator.serviceWorker.ready;
        setSwRegistration(registration);
      }

      // Get VAPID public key from backend
      console.log('[Notifications] Fetching VAPID key...');
      const keyResponse = await axios.get(`${API_URL}/api/notifications/vapid-public-key`, {
        withCredentials: true
      });
      const vapidPublicKey = keyResponse.data.publicKey;

      if (!vapidPublicKey) {
        setLoading(false);
        return { success: false, error: 'VAPID key not configured on server' };
      }

      // If a stale subscription already exists, reuse or reset it
      let sub = await registration.pushManager.getSubscription();
      if (!sub) {
        console.log('[Notifications] Subscribing to push manager...');
        sub = await registration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: urlBase64ToUint8Array(vapidPublicKey)
        });
      }
      console.log('[Notifications] Push subscription ready');

      // Send subscription to backend
      const subJson = sub.toJSON();
      await axios.post(`${API_URL}/api/notifications/subscribe`, {
        endpoint: subJson.endpoint,
        keys: {
          p256dh: subJson.keys.p256dh,
          auth: subJson.keys.auth
        }
      }, { withCredentials: true });
      console.log('[Notifications] Subscription saved to backend');

      setSubscription(sub);
      setIsSubscribed(true);
      setLoading(false);

      return { success: true };
    } catch (error) {
      console.error('[Notifications] Subscription failed:', error);
      setLoading(false);
      return { success: false, error: error.message || 'Unknown error occurred' };
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

  const value = useMemo(() => ({
    isSupported,
    permission,
    isSubscribed,
    loading,
    subscribe,
    unsubscribe,
    sendTestNotification
  }), [isSupported, permission, isSubscribed, loading, subscribe, unsubscribe, sendTestNotification]);

  return (
    <NotificationContext.Provider value={value}>
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

import { useState, useEffect, useCallback } from 'react';
import { signOut as amplifySignOut } from '@aws-amplify/auth';
import { getCurrentUserInfo, isAuthenticated, UserInfo } from '../utils/auth';

/**
 * Hook to manage authentication state
 */
export function useAuth() {
  const [user, setUser] = useState<UserInfo | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [authenticated, setAuthenticated] = useState<boolean>(false);

  const checkAuth = useCallback(async () => {
    try {
      setLoading(true);
      const isAuth = await isAuthenticated();
      setAuthenticated(isAuth);

      if (isAuth) {
        const userInfo = await getCurrentUserInfo();
        setUser(userInfo);
      } else {
        setUser(null);
      }
    } catch (error) {
      console.error('Error checking auth:', error);
      setAuthenticated(false);
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const signOut = useCallback(async () => {
    try {
      await amplifySignOut();
      setUser(null);
      setAuthenticated(false);
    } catch (error) {
      console.error('Error signing out:', error);
    }
  }, []);

  return {
    user,
    loading,
    authenticated,
    signOut,
    refetch: checkAuth,
  };
}

export default useAuth;

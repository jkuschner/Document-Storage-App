import { fetchAuthSession, getCurrentUser, fetchUserAttributes } from '@aws-amplify/auth';

export interface UserInfo {
  userId: string;
  email?: string;
  emailVerified?: boolean;
  sub: string; // Cognito user sub (unique identifier)
}

/**
 * Get the current authenticated user's ID
 * Returns the Cognito 'sub' which is used as userId in the backend
 */
export async function getCurrentUserId(): Promise<string | null> {
  try {
    const user = await getCurrentUser();
    return user.userId; // This is the 'sub' from Cognito
  } catch (error) {
    console.error('Failed to get current user ID:', error);
    return null;
  }
}

/**
 * Get comprehensive user information from Cognito
 */
export async function getCurrentUserInfo(): Promise<UserInfo | null> {
  try {
    const [user, attributes] = await Promise.all([
      getCurrentUser(),
      fetchUserAttributes(),
    ]);

    return {
      userId: user.userId,
      email: attributes.email,
      emailVerified: attributes.email_verified === 'true',
      sub: user.userId,
    };
  } catch (error) {
    console.error('Failed to get user info:', error);
    return null;
  }
}

/**
 * Check if user is authenticated
 */
export async function isAuthenticated(): Promise<boolean> {
  try {
    const session = await fetchAuthSession();
    return !!session.tokens?.idToken;
  } catch {
    return false;
  }
}

/**
 * Get the current auth session
 */
export async function getAuthSession() {
  try {
    return await fetchAuthSession();
  } catch (error) {
    console.error('Failed to get auth session:', error);
    return null;
  }
}

/**
 * Get JWT token for manual API calls
 */
export async function getIdToken(): Promise<string | null> {
  try {
    const session = await fetchAuthSession();
    return session.tokens?.idToken?.toString() || null;
  } catch (error) {
    console.error('Failed to get ID token:', error);
    return null;
  }
}

/**
 * Get access token
 */
export async function getAccessToken(): Promise<string | null> {
  try {
    const session = await fetchAuthSession();
    return session.tokens?.accessToken?.toString() || null;
  } catch (error) {
    console.error('Failed to get access token:', error);
    return null;
  }
}

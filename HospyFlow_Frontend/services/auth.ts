import * as SecureStore from 'expo-secure-store';
import { LoginResponse, User } from './types';

const TOKEN_KEY = 'hospyflow_access_token';
const REFRESH_TOKEN_KEY = 'hospyflow_refresh_token';
const USER_KEY = 'hospyflow_user';

/**
 * Authentication service for managing JWT tokens and user session
 */
export const authService = {
    /**
     * Store authentication tokens securely
     */
    async saveTokens(accessToken: string, refreshToken: string): Promise<void> {
        try {
            await SecureStore.setItemAsync(TOKEN_KEY, accessToken);
            await SecureStore.setItemAsync(REFRESH_TOKEN_KEY, refreshToken);
        } catch (error) {
            console.error('[Auth] Error saving tokens:', error);
            throw error;
        }
    },

    /**
     * Get the current access token
     */
    async getAccessToken(): Promise<string | null> {
        try {
            return await SecureStore.getItemAsync(TOKEN_KEY);
        } catch (error) {
            console.error('[Auth] Error getting access token:', error);
            return null;
        }
    },

    /**
     * Get the current refresh token
     */
    async getRefreshToken(): Promise<string | null> {
        try {
            return await SecureStore.getItemAsync(REFRESH_TOKEN_KEY);
        } catch (error) {
            console.error('[Auth] Error getting refresh token:', error);
            return null;
        }
    },

    /**
     * Store user data
     */
    async saveUser(user: User): Promise<void> {
        try {
            await SecureStore.setItemAsync(USER_KEY, JSON.stringify(user));
        } catch (error) {
            console.error('[Auth] Error saving user:', error);
            throw error;
        }
    },

    /**
     * Get stored user data
     */
    async getUser(): Promise<User | null> {
        try {
            const userJson = await SecureStore.getItemAsync(USER_KEY);
            return userJson ? JSON.parse(userJson) : null;
        } catch (error) {
            console.error('[Auth] Error getting user:', error);
            return null;
        }
    },

    /**
     * Save complete login response
     */
    async saveLoginData(loginResponse: LoginResponse): Promise<void> {
        await this.saveTokens(loginResponse.access, loginResponse.refresh);
        await this.saveUser(loginResponse.user);
    },

    /**
     * Clear all authentication data
     */
    async logout(): Promise<void> {
        try {
            await SecureStore.deleteItemAsync(TOKEN_KEY);
            await SecureStore.deleteItemAsync(REFRESH_TOKEN_KEY);
            await SecureStore.deleteItemAsync(USER_KEY);
            console.log('[Auth] Logged out successfully');
        } catch (error) {
            console.error('[Auth] Error during logout:', error);
            throw error;
        }
    },

    /**
     * Check if user is authenticated
     */
    async isAuthenticated(): Promise<boolean> {
        const token = await this.getAccessToken();
        return token !== null;
    },

    /**
     * Update access token (used after refresh)
     */
    async updateAccessToken(newAccessToken: string): Promise<void> {
        try {
            await SecureStore.setItemAsync(TOKEN_KEY, newAccessToken);
        } catch (error) {
            console.error('[Auth] Error updating access token:', error);
            throw error;
        }
    },
};

export default authService;

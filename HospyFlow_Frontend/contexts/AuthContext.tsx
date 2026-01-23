import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import authService from '@/services/auth';
import apiService from '@/services/api';
import type { User, LoginRequest } from '@/services/types';

// Role types
export type UserRole = 'NURSE' | 'DOCTOR' | 'LAB_TECH' | 'ADMIN';

// Auth context type
interface AuthContextType {
    user: User | null;
    isAuthenticated: boolean;
    isAdmin: boolean;
    isLoading: boolean;
    login: (credentials: LoginRequest) => Promise<void>;
    logout: () => Promise<void>;
    refreshUser: () => Promise<void>;
}

// Create context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Provider props
interface AuthProviderProps {
    children: ReactNode;
}

// Auth Provider Component
export function AuthProvider({ children }: AuthProviderProps) {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    // Check if user is authenticated on mount
    useEffect(() => {
        checkAuth();
    }, []);

    const checkAuth = async () => {
        try {
            const isAuth = await authService.isAuthenticated();
            if (isAuth) {
                const storedUser = await authService.getUser();
                setUser(storedUser);
            }
        } catch (error) {
            console.error('[AuthContext] Error checking auth:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const login = async (credentials: LoginRequest) => {
        try {
            const response = await apiService.login(credentials);
            setUser(response.user);
        } catch (error) {
            console.error('[AuthContext] Login error:', error);
            throw error;
        }
    };

    const logout = async () => {
        try {
            await apiService.logout();
            setUser(null);
        } catch (error) {
            console.error('[AuthContext] Logout error:', error);
            throw error;
        }
    };

    const refreshUser = async () => {
        try {
            const updatedUser = await apiService.getUserProfile();
            setUser(updatedUser);
        } catch (error) {
            console.error('[AuthContext] Refresh user error:', error);
            throw error;
        }
    };

    const value: AuthContextType = {
        user,
        isAuthenticated: !!user,
        isAdmin: user?.role === 'ADMIN',
        isLoading,
        login,
        logout,
        refreshUser,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// Custom hook to use auth context
export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}

// Role-based access helpers
export const isAdminRole = (role: UserRole): boolean => {
    return role === 'ADMIN';
};

export const isPersonnelRole = (role: UserRole): boolean => {
    return ['NURSE', 'DOCTOR', 'LAB_TECH'].includes(role);
};

export const getRoleLabel = (role: UserRole): string => {
    const labels: Record<UserRole, string> = {
        ADMIN: 'Administrateur',
        NURSE: 'Infirmier',
        DOCTOR: 'Médecin',
        LAB_TECH: 'Technicien de Laboratoire',
    };
    return labels[role] || role;
};

export default AuthContext;

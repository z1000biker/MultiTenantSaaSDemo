import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../utils/api';

const AuthContext = createContext(null);

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within AuthProvider');
    }
    return context;
};

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        checkAuth();
    }, []);

    const checkAuth = async () => {
        const token = localStorage.getItem('access_token');
        if (token) {
            try {
                const response = await authAPI.getCurrentUser();
                setUser(response.data);
            } catch (error) {
                localStorage.clear();
            }
        }
        setLoading(false);
    };

    const login = async (email, password, subdomain) => {
        localStorage.setItem('tenant_subdomain', subdomain);
        const response = await authAPI.login({ email, password });
        localStorage.setItem('access_token', response.data.access_token);
        localStorage.setItem('refresh_token', response.data.refresh_token);
        setUser(response.data.user);
        return response.data;
    };

    const register = async (data, subdomain) => {
        localStorage.setItem('tenant_subdomain', subdomain);
        const response = await authAPI.register(data);
        return response.data;
    };

    const logout = async () => {
        try {
            await authAPI.logout();
        } catch (error) {
            console.error('Logout error:', error);
        }
        localStorage.clear();
        setUser(null);
    };

    const value = {
        user,
        loading,
        login,
        register,
        logout,
        isAuthenticated: !!user,
        hasRole: (role) => {
            if (!user) return false;
            const roles = { member: 1, manager: 2, admin: 3 };
            return roles[user.role] >= roles[role];
        },
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

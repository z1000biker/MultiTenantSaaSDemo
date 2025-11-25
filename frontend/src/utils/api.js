import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

// Create axios instance
const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add tenant subdomain to requests
api.interceptors.request.use((config) => {
    // Get subdomain from hostname
    const hostname = window.location.hostname;
    const parts = hostname.split('.');

    // For development, use X-Tenant-Subdomain header
    if (hostname === 'localhost' || hostname.startsWith('127.0.0.1')) {
        const subdomain = localStorage.getItem('tenant_subdomain');
        if (subdomain) {
            config.headers['X-Tenant-Subdomain'] = subdomain;
        }
    }

    // Add auth token
    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
});

// Handle token refresh
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            const refreshToken = localStorage.getItem('refresh_token');
            if (refreshToken) {
                try {
                    const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {}, {
                        headers: { Authorization: `Bearer ${refreshToken}` }
                    });

                    localStorage.setItem('access_token', response.data.access_token);
                    originalRequest.headers.Authorization = `Bearer ${response.data.access_token}`;

                    return api(originalRequest);
                } catch (refreshError) {
                    localStorage.clear();
                    window.location.href = '/login';
                    return Promise.reject(refreshError);
                }
            }
        }

        return Promise.reject(error);
    }
);

// Auth API
export const authAPI = {
    register: (data) => api.post('/auth/register', data),
    login: (data) => api.post('/auth/login', data),
    logout: () => api.post('/auth/logout'),
    getCurrentUser: () => api.get('/auth/me'),
};

// Tenant API
export const tenantAPI = {
    create: (data) => api.post('/tenants', data),
    list: () => api.get('/tenants'),
    get: (id) => api.get(`/tenants/${id}`),
    update: (id, data) => api.put(`/tenants/${id}`, data),
    delete: (id) => api.delete(`/tenants/${id}`),
};

// User API
export const userAPI = {
    list: () => api.get('/users'),
    get: (id) => api.get(`/users/${id}`),
    update: (id, data) => api.put(`/users/${id}`, data),
    updateRole: (id, role) => api.put(`/users/${id}/role`, { role }),
    delete: (id) => api.delete(`/users/${id}`),
};

// Project API
export const projectAPI = {
    create: (data) => api.post('/projects', data),
    list: () => api.get('/projects'),
    get: (id) => api.get(`/projects/${id}`),
    update: (id, data) => api.put(`/projects/${id}`, data),
    delete: (id) => api.delete(`/projects/${id}`),
    addMember: (id, userId) => api.post(`/projects/${id}/members`, { user_id: userId }),
    removeMember: (id, userId) => api.delete(`/projects/${id}/members/${userId}`),
};

// List API
export const listAPI = {
    create: (projectId, data) => api.post(`/lists/projects/${projectId}/lists`, data),
    get: (id) => api.get(`/lists/${id}`),
    update: (id, data) => api.put(`/lists/${id}`, data),
    delete: (id) => api.delete(`/lists/${id}`),
    getByProject: (projectId) => api.get(`/lists/projects/${projectId}/lists`),
};

// Task API
export const taskAPI = {
    create: (listId, data) => api.post(`/tasks/lists/${listId}/tasks`, data),
    get: (id) => api.get(`/tasks/${id}`),
    update: (id, data) => api.put(`/tasks/${id}`, data),
    delete: (id) => api.delete(`/tasks/${id}`),
    move: (id, listId, position) => api.put(`/tasks/${id}/move`, { list_id: listId, position }),
    getByList: (listId) => api.get(`/tasks/lists/${listId}/tasks`),
    addComment: (id, content) => api.post(`/tasks/${id}/comments`, { content }),
};

export default api;

import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { tenantAPI } from '../../utils/api';
import './Auth.css';

const Register = () => {
    const navigate = useNavigate();
    const { register } = useAuth();
    const [step, setStep] = useState(1);
    const [formData, setFormData] = useState({
        // Tenant info
        tenant_name: '',
        subdomain: '',
        // Admin user info
        first_name: '',
        last_name: '',
        email: '',
        password: '',
        confirm_password: '',
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (formData.password !== formData.confirm_password) {
            setError('Passwords do not match');
            return;
        }

        setLoading(true);

        try {
            // Create tenant with admin user
            await tenantAPI.create({
                name: formData.tenant_name,
                subdomain: formData.subdomain,
                admin_email: formData.email,
                admin_password: formData.password,
                admin_first_name: formData.first_name,
                admin_last_name: formData.last_name,
            });

            // Navigate to login
            localStorage.setItem('tenant_subdomain', formData.subdomain);
            navigate('/login');
        } catch (err) {
            setError(err.response?.data?.error || 'Registration failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-card glass-card">
                <div className="auth-header">
                    <h1 className="auth-title">Create Your Workspace</h1>
                    <p className="text-muted">Get started with your team</p>
                </div>

                {error && (
                    <div className="alert alert-error">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="auth-form">
                    <div className="form-group">
                        <label className="form-label">Workspace Name</label>
                        <input
                            type="text"
                            name="tenant_name"
                            className="input"
                            placeholder="Acme Inc."
                            value={formData.tenant_name}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label className="form-label">Workspace Subdomain</label>
                        <input
                            type="text"
                            name="subdomain"
                            className="input"
                            placeholder="acme"
                            value={formData.subdomain}
                            onChange={handleChange}
                            required
                            pattern="[a-z0-9-]+"
                        />
                        <small className="text-muted">Only lowercase letters, numbers, and hyphens</small>
                    </div>

                    <div className="form-row">
                        <div className="form-group">
                            <label className="form-label">First Name</label>
                            <input
                                type="text"
                                name="first_name"
                                className="input"
                                placeholder="John"
                                value={formData.first_name}
                                onChange={handleChange}
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label className="form-label">Last Name</label>
                            <input
                                type="text"
                                name="last_name"
                                className="input"
                                placeholder="Doe"
                                value={formData.last_name}
                                onChange={handleChange}
                                required
                            />
                        </div>
                    </div>

                    <div className="form-group">
                        <label className="form-label">Email</label>
                        <input
                            type="email"
                            name="email"
                            className="input"
                            placeholder="john@acme.com"
                            value={formData.email}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label className="form-label">Password</label>
                        <input
                            type="password"
                            name="password"
                            className="input"
                            placeholder="••••••••"
                            value={formData.password}
                            onChange={handleChange}
                            required
                            minLength="8"
                        />
                    </div>

                    <div className="form-group">
                        <label className="form-label">Confirm Password</label>
                        <input
                            type="password"
                            name="confirm_password"
                            className="input"
                            placeholder="••••••••"
                            value={formData.confirm_password}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
                        {loading ? 'Creating workspace...' : 'Create Workspace'}
                    </button>
                </form>

                <div className="auth-footer">
                    <p className="text-muted">
                        Already have an account?{' '}
                        <Link to="/login" className="auth-link">
                            Sign in
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Register;

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { projectAPI } from '../../utils/api';
import './Dashboard.css';

const Dashboard = () => {
    const navigate = useNavigate();
    const { user, logout } = useAuth();
    const [projects, setProjects] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [newProject, setNewProject] = useState({ name: '', description: '', color: '#4A90E2' });

    useEffect(() => {
        loadProjects();
    }, []);

    const loadProjects = async () => {
        try {
            const response = await projectAPI.list();
            setProjects(response.data.projects);
        } catch (error) {
            console.error('Failed to load projects:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleCreateProject = async (e) => {
        e.preventDefault();
        try {
            await projectAPI.create(newProject);
            setShowCreateModal(false);
            setNewProject({ name: '', description: '', color: '#4A90E2' });
            loadProjects();
        } catch (error) {
            console.error('Failed to create project:', error);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center" style={{ minHeight: '100vh' }}>
                <div className="spinner"></div>
            </div>
        );
    }

    return (
        <div className="dashboard">
            <header className="dashboard-header glass-card">
                <div className="container">
                    <div className="flex justify-between items-center">
                        <div>
                            <h1 className="text-2xl font-bold">Projects</h1>
                            <p className="text-muted">Welcome back, {user?.first_name}!</p>
                        </div>
                        <div className="flex gap-md items-center">
                            <span className="badge">{user?.role}</span>
                            <button onClick={logout} className="btn btn-secondary">Logout</button>
                        </div>
                    </div>
                </div>
            </header>

            <main className="container" style={{ padding: 'var(--spacing-xl) var(--spacing-lg)' }}>
                <div className="dashboard-actions">
                    {(user?.role === 'admin' || user?.role === 'manager') && (
                        <button onClick={() => setShowCreateModal(true)} className="btn btn-primary">
                            + New Project
                        </button>
                    )}
                </div>

                <div className="projects-grid">
                    {projects.map((project) => (
                        <div
                            key={project.id}
                            className="project-card glass-card"
                            onClick={() => navigate(`/board/${project.id}`)}
                            style={{ borderLeft: `4px solid ${project.color}` }}
                        >
                            <h3 className="project-name">{project.name}</h3>
                            <p className="text-muted text-sm">{project.description || 'No description'}</p>
                            <div className="project-footer">
                                <span className="text-sm text-muted">{project.members?.length || 0} members</span>
                            </div>
                        </div>
                    ))}
                </div>

                {projects.length === 0 && (
                    <div className="empty-state">
                        <p className="text-muted">No projects yet. Create one to get started!</p>
                    </div>
                )}
            </main>

            {showCreateModal && (
                <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
                    <div className="modal glass-card" onClick={(e) => e.stopPropagation()}>
                        <h2 className="text-xl font-bold" style={{ marginBottom: 'var(--spacing-lg)' }}>Create New Project</h2>
                        <form onSubmit={handleCreateProject}>
                            <div className="form-group">
                                <label className="form-label">Project Name</label>
                                <input
                                    type="text"
                                    className="input"
                                    value={newProject.name}
                                    onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                                    required
                                />
                            </div>
                            <div className="form-group">
                                <label className="form-label">Description</label>
                                <textarea
                                    className="input"
                                    rows="3"
                                    value={newProject.description}
                                    onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                                />
                            </div>
                            <div className="form-group">
                                <label className="form-label">Color</label>
                                <input
                                    type="color"
                                    className="input"
                                    value={newProject.color}
                                    onChange={(e) => setNewProject({ ...newProject, color: e.target.value })}
                                />
                            </div>
                            <div className="flex gap-md justify-end">
                                <button type="button" onClick={() => setShowCreateModal(false)} className="btn btn-secondary">
                                    Cancel
                                </button>
                                <button type="submit" className="btn btn-primary">Create</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Dashboard;

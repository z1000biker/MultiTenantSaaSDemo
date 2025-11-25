import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { projectAPI, listAPI, taskAPI } from '../../utils/api';
import './Board.css';

const Board = () => {
    const { projectId } = useParams();
    const navigate = useNavigate();
    const [project, setProject] = useState(null);
    const [lists, setLists] = useState([]);
    const [loading, setLoading] = useState(true);
    const [newListName, setNewListName] = useState('');
    const [showNewList, setShowNewList] = useState(false);

    useEffect(() => {
        loadBoard();
    }, [projectId]);

    const loadBoard = async () => {
        try {
            const [projectRes, listsRes] = await Promise.all([
                projectAPI.get(projectId),
                listAPI.getByProject(projectId),
            ]);
            setProject(projectRes.data);
            setLists(listsRes.data.lists);
        } catch (error) {
            console.error('Failed to load board:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleCreateList = async (e) => {
        e.preventDefault();
        if (!newListName.trim()) return;

        try {
            await listAPI.create(projectId, { name: newListName });
            setNewListName('');
            setShowNewList(false);
            loadBoard();
        } catch (error) {
            console.error('Failed to create list:', error);
        }
    };

    const handleCreateTask = async (listId, title) => {
        try {
            await taskAPI.create(listId, { title });
            loadBoard();
        } catch (error) {
            console.error('Failed to create task:', error);
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
        <div className="board">
            <header className="board-header glass-card">
                <div className="container flex justify-between items-center">
                    <div className="flex items-center gap-md">
                        <button onClick={() => navigate('/dashboard')} className="btn btn-secondary">← Back</button>
                        <h1 className="text-2xl font-bold">{project?.name}</h1>
                    </div>
                </div>
            </header>

            <div className="board-content">
                <div className="lists-container">
                    {lists.map((list) => (
                        <div key={list.id} className="list glass-card">
                            <div className="list-header">
                                <h3 className="list-title">{list.name}</h3>
                                <span className="text-muted text-sm">{list.tasks?.length || 0} tasks</span>
                            </div>

                            <div className="tasks">
                                {list.tasks?.map((task) => (
                                    <div key={task.id} className="task-card glass-card">
                                        <h4 className="task-title">{task.title}</h4>
                                        {task.description && <p className="text-sm text-muted">{task.description}</p>}
                                        {task.assignee && (
                                            <div className="task-assignee">
                                                <span className="text-sm">{task.assignee.full_name}</span>
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>

                            <button
                                className="btn btn-secondary btn-block"
                                onClick={() => {
                                    const title = prompt('Task title:');
                                    if (title) handleCreateTask(list.id, title);
                                }}
                            >
                                + Add Task
                            </button>
                        </div>
                    ))}

                    {showNewList ? (
                        <div className="list glass-card">
                            <form onSubmit={handleCreateList}>
                                <input
                                    type="text"
                                    className="input"
                                    placeholder="List name..."
                                    value={newListName}
                                    onChange={(e) => setNewListName(e.target.value)}
                                    autoFocus
                                />
                                <div className="flex gap-sm" style={{ marginTop: 'var(--spacing-sm)' }}>
                                    <button type="submit" className="btn btn-primary">Add</button>
                                    <button type="button" onClick={() => setShowNewList(false)} className="btn btn-secondary">
                                        Cancel
                                    </button>
                                </div>
                            </form>
                        </div>
                    ) : (
                        <button className="add-list-btn glass-card" onClick={() => setShowNewList(true)}>
                            + Add List
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Board;

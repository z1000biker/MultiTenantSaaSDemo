"""Task model - stored in tenant-specific schema"""
from datetime import datetime
from models import db


class Task(db.Model):
    """Task/Card model for Kanban boards"""
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    list_id = db.Column(db.Integer, db.ForeignKey('lists.id'), nullable=False)
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    position = db.Column(db.Integer, nullable=False, default=0)
    
    # Task metadata
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    labels = db.Column(db.JSON, default=list)  # Array of label strings
    due_date = db.Column(db.DateTime)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    completed_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    list = db.relationship('List', back_populates='tasks')
    assignee = db.relationship('User', back_populates='assigned_tasks', foreign_keys=[assignee_id])
    comments = db.relationship('Comment', back_populates='task', cascade='all, delete-orphan', order_by='Comment.created_at')
    
    def __repr__(self):
        return f'<Task {self.title}>'
    
    def to_dict(self, include_comments=False):
        """Convert task to dictionary"""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'list_id': self.list_id,
            'assignee_id': self.assignee_id,
            'assignee': self.assignee.to_dict(include_email=False) if self.assignee else None,
            'position': self.position,
            'priority': self.priority,
            'labels': self.labels or [],
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed': self.completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_comments:
            data['comments'] = [comment.to_dict() for comment in self.comments]
        
        return data


class Comment(db.Model):
    """Comment model for tasks"""
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    task = db.relationship('Task', back_populates='comments')
    user = db.relationship('User')
    
    def __repr__(self):
        return f'<Comment on Task {self.task_id}>'
    
    def to_dict(self):
        """Convert comment to dictionary"""
        return {
            'id': self.id,
            'content': self.content,
            'task_id': self.task_id,
            'user_id': self.user_id,
            'user': self.user.to_dict(include_email=False) if self.user else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

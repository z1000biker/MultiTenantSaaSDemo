"""List model - stored in tenant-specific schema"""
from datetime import datetime
from models import db


class List(db.Model):
    """List/Column model for Kanban boards"""
    __tablename__ = 'lists'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    position = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    project = db.relationship('Project', back_populates='lists')
    tasks = db.relationship('Task', back_populates='list', cascade='all, delete-orphan', order_by='Task.position')
    
    def __repr__(self):
        return f'<List {self.name}>'
    
    def to_dict(self, include_tasks=False):
        """Convert list to dictionary"""
        data = {
            'id': self.id,
            'name': self.name,
            'project_id': self.project_id,
            'position': self.position,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_tasks:
            data['tasks'] = [task.to_dict() for task in self.tasks]
        
        return data

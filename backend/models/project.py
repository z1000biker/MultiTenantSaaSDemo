"""Project model - stored in tenant-specific schema"""
from datetime import datetime
from models import db


# Association table for project members
project_members = db.Table('project_members',
    db.Column('project_id', db.Integer, db.ForeignKey('projects.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('added_at', db.DateTime, default=datetime.utcnow)
)


class Project(db.Model):
    """Project/Board model"""
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Color/theme for visual customization
    color = db.Column(db.String(7), default='#4A90E2')  # Hex color
    
    # Relationships
    owner = db.relationship('User', back_populates='created_projects', foreign_keys=[owner_id])
    members = db.relationship('User', secondary=project_members, backref='projects')
    lists = db.relationship('List', back_populates='project', cascade='all, delete-orphan', order_by='List.position')
    
    def __repr__(self):
        return f'<Project {self.name}>'
    
    def to_dict(self, include_lists=False, include_members=False):
        """Convert project to dictionary"""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'owner_id': self.owner_id,
            'owner': self.owner.to_dict(include_email=False) if self.owner else None,
            'is_archived': self.is_archived,
            'color': self.color,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_members:
            data['members'] = [member.to_dict(include_email=False) for member in self.members]
        
        if include_lists:
            data['lists'] = [lst.to_dict(include_tasks=True) for lst in self.lists]
        
        return data
    
    def is_member(self, user):
        """Check if user is a member of this project"""
        return user in self.members or user.id == self.owner_id

"""User model - stored in tenant-specific schema"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from models import db


class User(db.Model):
    """User model with role-based access control"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='member')  # admin, manager, member
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    created_projects = db.relationship('Project', back_populates='owner', foreign_keys='Project.owner_id')
    assigned_tasks = db.relationship('Task', back_populates='assignee', foreign_keys='Task.assignee_id')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_email=True):
        """Convert user to dictionary"""
        data = {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': f'{self.first_name} {self.last_name}',
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        if include_email:
            data['email'] = self.email
        return data
    
    def has_role(self, role):
        """Check if user has specific role or higher"""
        role_hierarchy = {'member': 1, 'manager': 2, 'admin': 3}
        return role_hierarchy.get(self.role, 0) >= role_hierarchy.get(role, 0)

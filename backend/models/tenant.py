"""Tenant model - stored in master database"""
from datetime import datetime
from models import db


class Tenant(db.Model):
    """Tenant model for multi-tenant architecture"""
    __tablename__ = 'tenants'
    __bind_key__ = None  # Uses default/master database
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subdomain = db.Column(db.String(50), unique=True, nullable=False, index=True)
    schema_name = db.Column(db.String(63), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Metadata
    contact_email = db.Column(db.String(120))
    max_users = db.Column(db.Integer, default=10)
    
    def __repr__(self):
        return f'<Tenant {self.subdomain}>'
    
    def to_dict(self):
        """Convert tenant to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'subdomain': self.subdomain,
            'schema_name': self.schema_name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'contact_email': self.contact_email,
            'max_users': self.max_users
        }
    
    @staticmethod
    def generate_schema_name(subdomain):
        """Generate schema name from subdomain"""
        # Ensure schema name is valid PostgreSQL identifier
        schema = subdomain.lower().replace('-', '_')
        return f'tenant_{schema}'

"""Database initialization script for production deployment"""
import os
from app import create_app
from models import db
from models.tenant import Tenant

def init_database():
    """Initialize the master database with required tables"""
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✓ Database tables created successfully!")
        
        # Verify tables exist
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"✓ Created tables: {', '.join(tables)}")
        
        print("\n✅ Database initialization complete!")
        print("You can now create tenants via the API or web interface.")

if __name__ == '__main__':
    init_database()

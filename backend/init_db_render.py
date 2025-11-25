#!/usr/bin/env python
"""
Database initialization script for Render deployment.
Run this once after deploying to create all database tables.

Usage:
    python init_db_render.py
"""
import os
import sys

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db
from sqlalchemy import inspect, text

def init_database():
    """Initialize the master database with required tables"""
    print("=" * 60)
    print("DATABASE INITIALIZATION FOR RENDER")
    print("=" * 60)
    
    app = create_app('production')
    
    with app.app_context():
        try:
            # Test database connection
            print("\n1️⃣  Testing database connection...")
            db.session.execute(text('SELECT 1'))
            print("   ✅ Database connection successful!")
            
            # Check existing tables
            print("\n2️⃣  Checking existing tables...")
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            if existing_tables:
                print(f"   ℹ️  Found {len(existing_tables)} existing tables:")
                for table in existing_tables:
                    print(f"      - {table}")
            else:
                print("   ℹ️  No existing tables found")
            
            # Create all tables
            print("\n3️⃣  Creating database tables...")
            db.create_all()
            print("   ✅ Tables created successfully!")
            
            # Verify tables were created
            print("\n4️⃣  Verifying table creation...")
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if tables:
                print(f"   ✅ Successfully created {len(tables)} tables:")
                for table in tables:
                    print(f"      - {table}")
            else:
                print("   ⚠️  Warning: No tables found after creation")
            
            print("\n" + "=" * 60)
            print("✅ DATABASE INITIALIZATION COMPLETE!")
            print("=" * 60)
            print("\nNext steps:")
            print("1. Visit your frontend URL")
            print("2. Click 'Create Workspace' to register first tenant")
            print("3. Login and start using the application")
            print("\n")
            
        except Exception as e:
            print(f"\n❌ ERROR: Database initialization failed!")
            print(f"   Error: {str(e)}")
            print("\nTroubleshooting:")
            print("1. Check your DATABASE_URL environment variable")
            print("2. Ensure Neon database is accessible")
            print("3. Verify database credentials are correct")
            sys.exit(1)

if __name__ == '__main__':
    init_database()

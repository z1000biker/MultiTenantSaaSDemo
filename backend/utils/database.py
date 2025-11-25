"""Database utilities for multi-tenant operations"""
from sqlalchemy import text
from models import db


def create_tenant_schema(schema_name):
    """
    Create a new schema for a tenant
    
    Args:
        schema_name: Name of the schema to create
    """
    try:
        # Create schema
        db.session.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
        db.session.commit()
        
        # Set search_path to new schema
        db.session.execute(text(f"SET search_path TO {schema_name}, public"))
        db.session.commit()
        
        # Create tables in the new schema
        # Import models here to avoid circular imports
        from models.user import User
        from models.project import Project, project_members
        from models.list import List
        from models.task import Task, Comment
        
        # Create all tables
        db.create_all()
        
        # Reset search_path
        db.session.execute(text("SET search_path TO public"))
        db.session.commit()
        
        return True
    except Exception as e:
        db.session.rollback()
        raise Exception(f'Failed to create tenant schema: {str(e)}')


def delete_tenant_schema(schema_name):
    """
    Delete a tenant schema and all its data
    
    Args:
        schema_name: Name of the schema to delete
    """
    try:
        # Drop schema and all objects in it
        db.session.execute(text(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE"))
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        raise Exception(f'Failed to delete tenant schema: {str(e)}')


def schema_exists(schema_name):
    """
    Check if a schema exists
    
    Args:
        schema_name: Name of the schema to check
    
    Returns:
        bool: True if schema exists
    """
    result = db.session.execute(
        text("SELECT schema_name FROM information_schema.schemata WHERE schema_name = :schema"),
        {'schema': schema_name}
    )
    return result.fetchone() is not None


def get_tenant_stats(schema_name):
    """
    Get statistics for a tenant
    
    Args:
        schema_name: Name of the tenant schema
    
    Returns:
        dict: Statistics including user count, project count, task count
    """
    try:
        # Set search_path to tenant schema
        db.session.execute(text(f"SET search_path TO {schema_name}, public"))
        db.session.commit()
        
        # Import models
        from models.user import User
        from models.project import Project
        from models.task import Task
        
        # Get counts
        stats = {
            'users': User.query.count(),
            'projects': Project.query.count(),
            'tasks': Task.query.count(),
            'active_tasks': Task.query.filter_by(completed=False).count()
        }
        
        # Reset search_path
        db.session.execute(text("SET search_path TO public"))
        db.session.commit()
        
        return stats
    except Exception as e:
        db.session.rollback()
        return {'error': str(e)}

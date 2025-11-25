"""Role-Based Access Control (RBAC) decorators and utilities"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from models.user import User


def require_role(*allowed_roles):
    """
    Decorator to require specific roles for route access
    Usage: @require_role('admin') or @require_role('admin', 'manager')
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Verify JWT token
            verify_jwt_in_request()
            
            # Get current user
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user or not user.is_active:
                return jsonify({'error': 'User not found or inactive'}), 401
            
            # Check if user has required role
            if user.role not in allowed_roles:
                return jsonify({
                    'error': 'Insufficient permissions',
                    'required_roles': list(allowed_roles),
                    'your_role': user.role
                }), 403
            
            return fn(*args, **kwargs)
        
        return wrapper
    return decorator


def require_admin(fn):
    """Decorator to require admin role"""
    return require_role('admin')(fn)


def require_manager(fn):
    """Decorator to require manager or admin role"""
    return require_role('admin', 'manager')(fn)


def get_current_user():
    """Get current authenticated user"""
    try:
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        return User.query.get(current_user_id)
    except:
        return None


def check_permission(user, resource, action):
    """
    Check if user has permission to perform action on resource
    
    Args:
        user: User object
        resource: Resource object (Project, Task, etc.)
        action: Action string ('view', 'edit', 'delete')
    
    Returns:
        bool: True if user has permission
    """
    # Admin can do anything
    if user.role == 'admin':
        return True
    
    # Check resource-specific permissions
    resource_type = type(resource).__name__
    
    if resource_type == 'Project':
        # Owner can do anything
        if resource.owner_id == user.id:
            return True
        
        # Manager can edit/delete projects they're members of
        if user.role == 'manager' and resource.is_member(user):
            return action in ['view', 'edit', 'delete']
        
        # Members can only view
        if resource.is_member(user):
            return action == 'view'
    
    elif resource_type == 'Task':
        # Check project membership first
        project = resource.list.project
        if not project.is_member(user):
            return False
        
        # Manager can do anything
        if user.role == 'manager':
            return True
        
        # Members can edit/delete their own tasks
        if action in ['edit', 'delete']:
            return resource.assignee_id == user.id
        
        # Members can view all tasks in their projects
        return action == 'view'
    
    return False

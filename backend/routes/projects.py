"""Project management routes"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db
from models.project import Project
from models.user import User
from middleware.rbac import get_current_user, check_permission

projects_bp = Blueprint('projects', __name__, url_prefix='/api/projects')


@projects_bp.route('', methods=['POST'])
@jwt_required()
def create_project():
    """Create a new project"""
    current_user = get_current_user()
    
    # Check if user has permission to create projects
    if current_user.role not in ['admin', 'manager']:
        return jsonify({'error': 'Only admins and managers can create projects'}), 403
    
    data = request.get_json()
    
    if not data.get('name'):
        return jsonify({'error': 'Project name is required'}), 400
    
    project = Project(
        name=data['name'],
        description=data.get('description', ''),
        owner_id=current_user.id,
        color=data.get('color', '#4A90E2')
    )
    
    # Add owner as member
    project.members.append(current_user)
    
    try:
        db.session.add(project)
        db.session.commit()
        
        return jsonify({
            'message': 'Project created successfully',
            'project': project.to_dict(include_members=True)
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create project: {str(e)}'}), 500


@projects_bp.route('', methods=['GET'])
@jwt_required()
def list_projects():
    """List all projects user has access to"""
    current_user = get_current_user()
    
    # Get projects where user is owner or member
    projects = Project.query.filter(
        (Project.owner_id == current_user.id) | 
        (Project.members.any(id=current_user.id))
    ).filter_by(is_archived=False).all()
    
    return jsonify({
        'projects': [p.to_dict(include_members=True) for p in projects],
        'total': len(projects)
    }), 200


@projects_bp.route('/<int:project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    """Get project details with lists and tasks"""
    current_user = get_current_user()
    project = Project.query.get(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    if not check_permission(current_user, project, 'view'):
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify(project.to_dict(include_lists=True, include_members=True)), 200


@projects_bp.route('/<int:project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    """Update project"""
    current_user = get_current_user()
    project = Project.query.get(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    if not check_permission(current_user, project, 'edit'):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    if 'name' in data:
        project.name = data['name']
    if 'description' in data:
        project.description = data['description']
    if 'color' in data:
        project.color = data['color']
    if 'is_archived' in data and current_user.role in ['admin', 'manager']:
        project.is_archived = data['is_archived']
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Project updated successfully',
            'project': project.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Update failed: {str(e)}'}), 500


@projects_bp.route('/<int:project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    """Delete project"""
    current_user = get_current_user()
    project = Project.query.get(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    if not check_permission(current_user, project, 'delete'):
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        db.session.delete(project)
        db.session.commit()
        return jsonify({'message': 'Project deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Delete failed: {str(e)}'}), 500


@projects_bp.route('/<int:project_id>/members', methods=['POST'])
@jwt_required()
def add_member(project_id):
    """Add member to project"""
    current_user = get_current_user()
    project = Project.query.get(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    if not check_permission(current_user, project, 'edit'):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if user in project.members:
        return jsonify({'error': 'User is already a member'}), 409
    
    project.members.append(user)
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Member added successfully',
            'project': project.to_dict(include_members=True)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to add member: {str(e)}'}), 500


@projects_bp.route('/<int:project_id>/members/<int:user_id>', methods=['DELETE'])
@jwt_required()
def remove_member(project_id, user_id):
    """Remove member from project"""
    current_user = get_current_user()
    project = Project.query.get(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    if not check_permission(current_user, project, 'edit'):
        return jsonify({'error': 'Access denied'}), 403
    
    # Cannot remove owner
    if user_id == project.owner_id:
        return jsonify({'error': 'Cannot remove project owner'}), 400
    
    user = User.query.get(user_id)
    if not user or user not in project.members:
        return jsonify({'error': 'User is not a member'}), 404
    
    project.members.remove(user)
    
    try:
        db.session.commit()
        return jsonify({'message': 'Member removed successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to remove member: {str(e)}'}), 500

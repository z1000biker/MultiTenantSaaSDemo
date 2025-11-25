"""List management routes"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db
from models.list import List
from models.project import Project
from middleware.rbac import get_current_user, check_permission

lists_bp = Blueprint('lists', __name__, url_prefix='/api/lists')


@lists_bp.route('/<int:list_id>', methods=['GET'])
@jwt_required()
def get_list(list_id):
    """Get list with tasks"""
    current_user = get_current_user()
    lst = List.query.get(list_id)
    
    if not lst:
        return jsonify({'error': 'List not found'}), 404
    
    if not check_permission(current_user, lst.project, 'view'):
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify(lst.to_dict(include_tasks=True)), 200


@lists_bp.route('/<int:list_id>', methods=['PUT'])
@jwt_required()
def update_list(list_id):
    """Update list"""
    current_user = get_current_user()
    lst = List.query.get(list_id)
    
    if not lst:
        return jsonify({'error': 'List not found'}), 404
    
    if not check_permission(current_user, lst.project, 'edit'):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    if 'name' in data:
        lst.name = data['name']
    if 'position' in data:
        lst.position = data['position']
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'List updated successfully',
            'list': lst.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Update failed: {str(e)}'}), 500


@lists_bp.route('/<int:list_id>', methods=['DELETE'])
@jwt_required()
def delete_list(list_id):
    """Delete list"""
    current_user = get_current_user()
    lst = List.query.get(list_id)
    
    if not lst:
        return jsonify({'error': 'List not found'}), 404
    
    if not check_permission(current_user, lst.project, 'edit'):
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        db.session.delete(lst)
        db.session.commit()
        return jsonify({'message': 'List deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Delete failed: {str(e)}'}), 500


# Project-specific list routes
@lists_bp.route('/projects/<int:project_id>/lists', methods=['POST'])
@jwt_required()
def create_list(project_id):
    """Create a new list in project"""
    current_user = get_current_user()
    project = Project.query.get(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    if not check_permission(current_user, project, 'edit'):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    if not data.get('name'):
        return jsonify({'error': 'List name is required'}), 400
    
    # Get max position
    max_position = db.session.query(db.func.max(List.position)).filter_by(project_id=project_id).scalar() or -1
    
    lst = List(
        name=data['name'],
        project_id=project_id,
        position=max_position + 1
    )
    
    try:
        db.session.add(lst)
        db.session.commit()
        
        return jsonify({
            'message': 'List created successfully',
            'list': lst.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create list: {str(e)}'}), 500


@lists_bp.route('/projects/<int:project_id>/lists', methods=['GET'])
@jwt_required()
def get_project_lists(project_id):
    """Get all lists for a project"""
    current_user = get_current_user()
    project = Project.query.get(project_id)
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    if not check_permission(current_user, project, 'view'):
        return jsonify({'error': 'Access denied'}), 403
    
    lists = List.query.filter_by(project_id=project_id).order_by(List.position).all()
    
    return jsonify({
        'lists': [lst.to_dict(include_tasks=True) for lst in lists],
        'total': len(lists)
    }), 200

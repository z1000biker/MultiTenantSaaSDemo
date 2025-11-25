"""User management routes"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db
from models.user import User
from middleware.rbac import require_role, get_current_user

users_bp = Blueprint('users', __name__, url_prefix='/api/users')


@users_bp.route('', methods=['GET'])
@jwt_required()
@require_role('admin', 'manager')
def list_users():
    """List all users in tenant"""
    users = User.query.filter_by(is_active=True).all()
    
    return jsonify({
        'users': [user.to_dict() for user in users],
        'total': len(users)
    }), 200


@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get user details"""
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict()), 200


@users_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Update user information"""
    current_user = get_current_user()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Users can only update themselves unless they're admin
    if current_user.id != user_id and current_user.role != 'admin':
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    data = request.get_json()
    
    # Update allowed fields
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'email' in data and current_user.role == 'admin':
        # Check if email is already taken
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user_id:
            return jsonify({'error': 'Email already taken'}), 409
        user.email = data['email']
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Update failed: {str(e)}'}), 500


@users_bp.route('/<int:user_id>/role', methods=['PUT'])
@jwt_required()
@require_role('admin')
def update_user_role(user_id):
    """Update user role (admin only)"""
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    new_role = data.get('role')
    
    if new_role not in ['admin', 'manager', 'member']:
        return jsonify({'error': 'Invalid role'}), 400
    
    user.role = new_role
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'User role updated successfully',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Update failed: {str(e)}'}), 500


@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
@require_role('admin')
def delete_user(user_id):
    """Delete user (soft delete - set inactive)"""
    current_user = get_current_user()
    
    # Prevent self-deletion
    if current_user.id == user_id:
        return jsonify({'error': 'Cannot delete yourself'}), 400
    
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Soft delete
    user.is_active = False
    
    try:
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Delete failed: {str(e)}'}), 500

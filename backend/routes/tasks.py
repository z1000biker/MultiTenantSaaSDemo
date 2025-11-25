"""Task management routes"""
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db
from models.task import Task, Comment
from models.list import List
from middleware.rbac import get_current_user, check_permission

tasks_bp = Blueprint('tasks', __name__, url_prefix='/api/tasks')


@tasks_bp.route('/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """Get task details with comments"""
    current_user = get_current_user()
    task = Task.query.get(task_id)
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    if not check_permission(current_user, task, 'view'):
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify(task.to_dict(include_comments=True)), 200


@tasks_bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """Update task"""
    current_user = get_current_user()
    task = Task.query.get(task_id)
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    if not check_permission(current_user, task, 'edit'):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'assignee_id' in data:
        task.assignee_id = data['assignee_id']
    if 'priority' in data:
        task.priority = data['priority']
    if 'labels' in data:
        task.labels = data['labels']
    if 'due_date' in data:
        task.due_date = datetime.fromisoformat(data['due_date']) if data['due_date'] else None
    if 'completed' in data:
        task.completed = data['completed']
        if task.completed:
            task.completed_at = datetime.utcnow()
        else:
            task.completed_at = None
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Task updated successfully',
            'task': task.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Update failed: {str(e)}'}), 500


@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """Delete task"""
    current_user = get_current_user()
    task = Task.query.get(task_id)
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    if not check_permission(current_user, task, 'delete'):
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        db.session.delete(task)
        db.session.commit()
        return jsonify({'message': 'Task deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Delete failed: {str(e)}'}), 500


@tasks_bp.route('/<int:task_id>/move', methods=['PUT'])
@jwt_required()
def move_task(task_id):
    """Move task to different list"""
    current_user = get_current_user()
    task = Task.query.get(task_id)
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    if not check_permission(current_user, task, 'edit'):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    new_list_id = data.get('list_id')
    new_position = data.get('position', 0)
    
    if not new_list_id:
        return jsonify({'error': 'list_id is required'}), 400
    
    new_list = List.query.get(new_list_id)
    if not new_list:
        return jsonify({'error': 'List not found'}), 404
    
    task.list_id = new_list_id
    task.position = new_position
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Task moved successfully',
            'task': task.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Move failed: {str(e)}'}), 500


# List-specific task routes
@tasks_bp.route('/lists/<int:list_id>/tasks', methods=['POST'])
@jwt_required()
def create_task(list_id):
    """Create a new task in list"""
    current_user = get_current_user()
    lst = List.query.get(list_id)
    
    if not lst:
        return jsonify({'error': 'List not found'}), 404
    
    if not check_permission(current_user, lst.project, 'view'):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    if not data.get('title'):
        return jsonify({'error': 'Task title is required'}), 400
    
    # Get max position
    max_position = db.session.query(db.func.max(Task.position)).filter_by(list_id=list_id).scalar() or -1
    
    task = Task(
        title=data['title'],
        description=data.get('description', ''),
        list_id=list_id,
        assignee_id=data.get('assignee_id'),
        priority=data.get('priority', 'medium'),
        labels=data.get('labels', []),
        position=max_position + 1
    )
    
    if data.get('due_date'):
        task.due_date = datetime.fromisoformat(data['due_date'])
    
    try:
        db.session.add(task)
        db.session.commit()
        
        return jsonify({
            'message': 'Task created successfully',
            'task': task.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create task: {str(e)}'}), 500


@tasks_bp.route('/lists/<int:list_id>/tasks', methods=['GET'])
@jwt_required()
def get_list_tasks(list_id):
    """Get all tasks for a list"""
    current_user = get_current_user()
    lst = List.query.get(list_id)
    
    if not lst:
        return jsonify({'error': 'List not found'}), 404
    
    if not check_permission(current_user, lst.project, 'view'):
        return jsonify({'error': 'Access denied'}), 403
    
    tasks = Task.query.filter_by(list_id=list_id).order_by(Task.position).all()
    
    return jsonify({
        'tasks': [task.to_dict() for task in tasks],
        'total': len(tasks)
    }), 200


# Comment routes
@tasks_bp.route('/<int:task_id>/comments', methods=['POST'])
@jwt_required()
def add_comment(task_id):
    """Add comment to task"""
    current_user = get_current_user()
    task = Task.query.get(task_id)
    
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    
    if not check_permission(current_user, task, 'view'):
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    if not data.get('content'):
        return jsonify({'error': 'Comment content is required'}), 400
    
    comment = Comment(
        content=data['content'],
        task_id=task_id,
        user_id=current_user.id
    )
    
    try:
        db.session.add(comment)
        db.session.commit()
        
        return jsonify({
            'message': 'Comment added successfully',
            'comment': comment.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to add comment: {str(e)}'}), 500

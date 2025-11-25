"""Tenant management routes"""
from flask import Blueprint, request, jsonify
from models import db
from models.tenant import Tenant
from models.user import User
from utils.database import create_tenant_schema, delete_tenant_schema, get_tenant_stats
from sqlalchemy import text

tenants_bp = Blueprint('tenants', __name__, url_prefix='/api/tenants')


@tenants_bp.route('', methods=['POST'])
def create_tenant():
    """Create a new tenant with admin user"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'subdomain', 'admin_email', 'admin_password', 'admin_first_name', 'admin_last_name']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    # Check if subdomain is already taken
    existing_tenant = Tenant.query.filter_by(subdomain=data['subdomain']).first()
    if existing_tenant:
        return jsonify({'error': 'Subdomain already taken'}), 409
    
    # Generate schema name
    schema_name = Tenant.generate_schema_name(data['subdomain'])
    
    try:
        # Create tenant in master database
        tenant = Tenant(
            name=data['name'],
            subdomain=data['subdomain'],
            schema_name=schema_name,
            contact_email=data.get('admin_email'),
            max_users=data.get('max_users', 10)
        )
        
        db.session.add(tenant)
        db.session.commit()
        
        # Create tenant schema
        create_tenant_schema(schema_name)
        
        # Set search_path to new tenant schema
        db.session.execute(text(f"SET search_path TO {schema_name}, public"))
        db.session.commit()
        
        # Create admin user in tenant schema
        admin_user = User(
            email=data['admin_email'],
            first_name=data['admin_first_name'],
            last_name=data['admin_last_name'],
            role='admin'
        )
        admin_user.set_password(data['admin_password'])
        
        db.session.add(admin_user)
        db.session.commit()
        
        # Reset search_path
        db.session.execute(text("SET search_path TO public"))
        db.session.commit()
        
        return jsonify({
            'message': 'Tenant created successfully',
            'tenant': tenant.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        # Try to cleanup if tenant was created
        try:
            if tenant.id:
                delete_tenant_schema(schema_name)
                db.session.delete(tenant)
                db.session.commit()
        except:
            pass
        
        return jsonify({'error': f'Failed to create tenant: {str(e)}'}), 500


@tenants_bp.route('', methods=['GET'])
def list_tenants():
    """List all tenants (for super admin)"""
    tenants = Tenant.query.all()
    
    return jsonify({
        'tenants': [tenant.to_dict() for tenant in tenants],
        'total': len(tenants)
    }), 200


@tenants_bp.route('/<int:tenant_id>', methods=['GET'])
def get_tenant(tenant_id):
    """Get tenant details with statistics"""
    tenant = Tenant.query.get(tenant_id)
    
    if not tenant:
        return jsonify({'error': 'Tenant not found'}), 404
    
    # Get tenant statistics
    stats = get_tenant_stats(tenant.schema_name)
    
    tenant_data = tenant.to_dict()
    tenant_data['stats'] = stats
    
    return jsonify(tenant_data), 200


@tenants_bp.route('/<int:tenant_id>', methods=['PUT'])
def update_tenant(tenant_id):
    """Update tenant information"""
    tenant = Tenant.query.get(tenant_id)
    
    if not tenant:
        return jsonify({'error': 'Tenant not found'}), 404
    
    data = request.get_json()
    
    # Update allowed fields
    if 'name' in data:
        tenant.name = data['name']
    if 'is_active' in data:
        tenant.is_active = data['is_active']
    if 'contact_email' in data:
        tenant.contact_email = data['contact_email']
    if 'max_users' in data:
        tenant.max_users = data['max_users']
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Tenant updated successfully',
            'tenant': tenant.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Update failed: {str(e)}'}), 500


@tenants_bp.route('/<int:tenant_id>', methods=['DELETE'])
def delete_tenant(tenant_id):
    """Delete tenant and all its data"""
    tenant = Tenant.query.get(tenant_id)
    
    if not tenant:
        return jsonify({'error': 'Tenant not found'}), 404
    
    schema_name = tenant.schema_name
    
    try:
        # Delete tenant schema and all data
        delete_tenant_schema(schema_name)
        
        # Delete tenant record
        db.session.delete(tenant)
        db.session.commit()
        
        return jsonify({'message': 'Tenant deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Delete failed: {str(e)}'}), 500

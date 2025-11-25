"""Main Flask application"""
import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from config import config
from models import db

# Import routes
from routes.auth import auth_bp
from routes.tenants import tenants_bp
from routes.users import users_bp
from routes.projects import projects_bp
from routes.lists import lists_bp
from routes.tasks import tasks_bp

# Import middleware
from middleware.tenant_middleware import TenantMiddleware


def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    JWTManager(app)
    Migrate(app, db)
    
    # Initialize multi-tenant middleware
    TenantMiddleware(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(tenants_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(lists_bp)
    app.register_blueprint(tasks_bp)
    
    # Initialize database tables on first run
    with app.app_context():
        try:
            # Check if tables exist by trying to query
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if not tables or 'tenants' not in tables:
                print("📦 Initializing database tables...")
                db.create_all()
                print("✅ Database tables created successfully!")
            else:
                print(f"✓ Database already initialized ({len(tables)} tables found)")
        except Exception as e:
            print(f"⚠️  Database initialization check failed: {e}")
            print("📦 Attempting to create tables...")
            try:
                db.create_all()
                print("✅ Database tables created successfully!")
            except Exception as create_error:
                print(f"❌ Failed to create tables: {create_error}")
    
    # Health check endpoint
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy', 'service': 'multi-tenant-saas'}), 200
    
    # Root endpoint
    @app.route('/')
    def index():
        return jsonify({
            'name': 'Multi-Tenant SaaS API',
            'version': '1.0.0',
            'description': 'Project management tool with multi-tenant architecture'
        }), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)

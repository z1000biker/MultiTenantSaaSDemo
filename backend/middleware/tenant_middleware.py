"""Multi-tenant middleware for schema-based tenant isolation"""
from flask import g, request
from sqlalchemy import text
from models import db
from models.tenant import Tenant


class TenantMiddleware:
    """Middleware to handle tenant identification and schema switching"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize middleware with Flask app"""
        app.before_request(self.before_request)
        app.teardown_appcontext(self.teardown)
    
    def before_request(self):
        """Extract tenant from request and set schema"""
        # Skip tenant detection for certain routes
        if self._should_skip_tenant_detection():
            return
        
        # Extract subdomain from request
        subdomain = self._extract_subdomain()
        
        if not subdomain:
            return {'error': 'Tenant subdomain is required'}, 400
        
        # Lookup tenant in master database
        tenant = Tenant.query.filter_by(subdomain=subdomain, is_active=True).first()
        
        if not tenant:
            return {'error': f'Tenant not found: {subdomain}'}, 404
        
        # Store tenant in Flask g object
        g.tenant = tenant
        
        # Set PostgreSQL search_path to tenant schema
        self._set_schema(tenant.schema_name)
    
    def _should_skip_tenant_detection(self):
        """Check if tenant detection should be skipped for this route"""
        # Skip for health checks, tenant creation, etc.
        skip_paths = ['/health', '/api/tenants']
        return any(request.path.startswith(path) for path in skip_paths)
    
    def _extract_subdomain(self):
        """Extract subdomain from request"""
        # Try to get from custom header first (useful for development)
        subdomain = request.headers.get('X-Tenant-Subdomain')
        
        if subdomain:
            return subdomain
        
        # Extract from host
        host = request.host.split(':')[0]  # Remove port if present
        parts = host.split('.')
        
        # If localhost or IP, check for subdomain in header
        if host in ['localhost', '127.0.0.1'] or host.startswith('192.168'):
            return request.headers.get('X-Tenant-Subdomain')
        
        # For production domains like tenant.example.com
        if len(parts) > 2:
            return parts[0]
        
        return None
    
    def _set_schema(self, schema_name):
        """Set PostgreSQL search_path to tenant schema"""
        try:
            # Set search_path for this connection
            db.session.execute(text(f"SET search_path TO {schema_name}, public"))
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise Exception(f'Failed to set schema: {str(e)}')
    
    def teardown(self, exception=None):
        """Reset schema after request"""
        if hasattr(g, 'tenant'):
            try:
                # Reset to public schema
                db.session.execute(text("SET search_path TO public"))
                db.session.commit()
            except:
                pass


def get_current_tenant():
    """Get current tenant from Flask g object"""
    return getattr(g, 'tenant', None)

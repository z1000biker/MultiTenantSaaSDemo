"""Basic tests for the application"""
import pytest
from app import create_app
from models import db


@pytest.fixture
def app():
    """Create and configure a test app instance"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client for the app"""
    return app.test_client()


def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'


def test_index_endpoint(client):
    """Test index endpoint"""
    response = client.get('/')
    assert response.status_code == 200
    assert 'Multi-Tenant SaaS API' in response.json['name']

"""
Testes básicos para o MultiSchema
"""
import pytest
import json
import tempfile
import os
from backend.app import create_app
from backend.database import db
from backend.models.user import User, Role


@pytest.fixture
def app():
    """Cria uma instância de teste da aplicação"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Cliente de teste para fazer requisições"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Runner de comandos CLI"""
    return app.test_cli_runner()


class TestUserAPI:
    """Testes para API de usuários"""
    
    def test_create_user(self, client):
        """Teste de criação de usuário"""
        user_data = {
            "username": "testuser",
            "email": "test@email.com",
            "password": "TestPass123"
        }
        
        response = client.post('/api/v1/user/', 
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['username'] == 'testuser'
        assert data['email'] == 'test@email.com'
        assert 'password' not in data  # Password não deve ser retornada
    
    def test_create_user_invalid_email(self, client):
        """Teste de criação com email inválido"""
        user_data = {
            "username": "testuser",
            "email": "invalid-email",
            "password": "TestPass123"
        }
        
        response = client.post('/api/v1/user/', 
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_create_user_weak_password(self, client):
        """Teste de criação com senha fraca"""
        user_data = {
            "username": "testuser",
            "email": "test@email.com",
            "password": "123"
        }
        
        response = client.post('/api/v1/user/', 
                             data=json.dumps(user_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_get_users(self, client):
        """Teste de listagem de usuários"""
        response = client.get('/api/v1/user/')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)


class TestSitesAPI:
    """Testes para API de sites"""
    
    def test_list_sites_empty(self, client):
        """Teste de listagem sem sites"""
        response = client.get('/api/v1/sites/')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['sites'] == []
    
    def test_create_site(self, client):
        """Teste de criação de site"""
        site_data = {
            "site_name": "testsite",
            "description": "Site de teste"
        }
        
        response = client.post('/api/v1/sites/',
                             data=json.dumps(site_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'message' in data
        assert data['site_config']['site_name'] == 'testsite'
    
    def test_create_site_invalid_name(self, client):
        """Teste de criação com nome inválido"""
        site_data = {
            "site_name": "si",  # Nome muito curto
            "description": "Site de teste"
        }
        
        response = client.post('/api/v1/sites/',
                             data=json.dumps(site_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data


class TestAuthUtils:
    """Testes para utilitários de autenticação"""
    
    def test_password_hashing(self):
        """Teste de hash de senha"""
        from backend.utils.auth import hash_password, verify_password
        
        password = "TestPassword123"
        hashed = hash_password(password)
        
        assert hashed != password  # Hash deve ser diferente da senha
        assert verify_password(password, hashed)  # Verificação deve funcionar
        assert not verify_password("wrong", hashed)  # Senha errada deve falhar
    
    def test_password_strength_validation(self):
        """Teste de validação de força da senha"""
        from backend.utils.auth import validate_password_strength
        
        # Senha forte
        strong_password = "StrongPass123"
        errors = validate_password_strength(strong_password)
        assert len(errors) == 0
        
        # Senha fraca
        weak_password = "123"
        errors = validate_password_strength(weak_password)
        assert len(errors) > 0


if __name__ == '__main__':
    pytest.main([__file__])
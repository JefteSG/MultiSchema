"""
Testes de integração para API REST
"""
import json
import pytest


class TestUserAPI:
    """Testes para API de usuários"""
    
    def test_create_user_success(self, client):
        """Teste de criação de usuário com sucesso"""
        user_data = {
            "username": "apiuser",
            "email": "api@example.com",
            "password": "ApiPass123"
        }
        
        response = client.post(
            '/api/v1/user/',
            data=json.dumps(user_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['username'] == 'apiuser'
        assert data['email'] == 'api@example.com'
        assert 'password' not in data
    
    def test_create_user_invalid_email(self, client):
        """Teste de criação com email inválido"""
        user_data = {
            "username": "testuser",
            "email": "invalid-email",
            "password": "TestPass123"
        }
        
        response = client.post(
            '/api/v1/user/',
            data=json.dumps(user_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_create_user_weak_password(self, client):
        """Teste de criação com senha fraca"""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "123"
        }
        
        response = client.post(
            '/api/v1/user/',
            data=json.dumps(user_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_get_users(self, client):
        """Teste de listagem de usuários"""
        response = client.get('/api/v1/user/')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
    
    def test_get_user_by_id_not_found(self, client):
        """Teste de busca de usuário inexistente"""
        response = client.get('/api/v1/user/99999')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data


class TestSitesAPI:
    """Testes para API de sites"""
    
    def test_list_sites_empty(self, client):
        """Teste de listagem sem sites"""
        response = client.get('/api/v1/sites/')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'sites' in data
        assert isinstance(data['sites'], list)
    
    def test_create_site_success(self, client):
        """Teste de criação de site com sucesso"""
        site_data = {
            "site_name": "testsite",
            "description": "Site de teste"
        }
        
        response = client.post(
            '/api/v1/sites/',
            data=json.dumps(site_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'message' in data
        assert 'site_config' in data
        assert data['site_config']['site_name'] == 'testsite'
    
    def test_create_site_invalid_name(self, client):
        """Teste de criação com nome inválido"""
        site_data = {
            "site_name": "ab",  # Nome muito curto
            "description": "Site de teste"
        }
        
        response = client.post(
            '/api/v1/sites/',
            data=json.dumps(site_data),
            content_type='application/json'
        )
        
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
        
        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("wrong", hashed)
    
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

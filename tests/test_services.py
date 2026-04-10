"""
Testes para a camada de Service (User)
"""
import pytest
from backend.services.user_service import UserService
from backend.models.user import User


class TestUserService:
    """Testes para UserService"""
    
    def test_validate_email_valid(self):
        """Teste de validação de email válido"""
        assert UserService.validate_email("test@example.com") is True
        assert UserService.validate_email("user.name+tag@domain.co.uk") is True
    
    def test_validate_email_invalid(self):
        """Teste de validação de email inválido"""
        assert UserService.validate_email("invalid") is False
        assert UserService.validate_email("@example.com") is False
        assert UserService.validate_email("test@") is False
    
    def test_validate_user_data_valid(self):
        """Teste de validação de dados válidos"""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "ValidPass123"
        }
        errors = UserService.validate_user_data(data)
        assert len(errors) == 0
    
    def test_validate_user_data_invalid_username(self):
        """Teste de validação com username inválido"""
        data = {
            "username": "ab",  # Muito curto
            "email": "test@example.com",
            "password": "ValidPass123"
        }
        errors = UserService.validate_user_data(data)
        assert len(errors) > 0
        assert any("Username" in error for error in errors)
    
    def test_validate_user_data_invalid_email(self):
        """Teste de validação com email inválido"""
        data = {
            "username": "testuser",
            "email": "invalid-email",
            "password": "ValidPass123"
        }
        errors = UserService.validate_user_data(data)
        assert len(errors) > 0
        assert any("email" in error.lower() for error in errors)
    
    def test_validate_user_data_weak_password(self):
        """Teste de validação com senha fraca"""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "123"  # Senha muito fraca
        }
        errors = UserService.validate_user_data(data)
        assert len(errors) > 0
    
    def test_get_all_users(self, session, sample_user):
        """Teste de listagem de usuários"""
        service = UserService(session)
        users = service.get_all_users()
        
        assert len(users) >= 1
        assert isinstance(users, list)
        assert isinstance(users[0], dict)
    
    def test_get_user_by_id(self, session, sample_user):
        """Teste de busca de usuário por ID"""
        service = UserService(session)
        user = service.get_user_by_id(sample_user.id)
        
        assert user is not None
        assert user['id'] == sample_user.id
        assert user['username'] == "testuser"
    
    def test_create_user_success(self, session):
        """Teste de criação de usuário com sucesso"""
        service = UserService(session)
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "NewPass123"
        }
        
        user = service.create_user(data)
        
        assert user['username'] == "newuser"
        assert user['email'] == "new@example.com"
        assert 'password' not in user  # Senha não deve ser retornada
    
    def test_create_user_duplicate_username(self, session, sample_user):
        """Teste de criação com username duplicado"""
        service = UserService(session)
        data = {
            "username": "testuser",  # Já existe
            "email": "other@example.com",
            "password": "Pass123"
        }
        
        with pytest.raises(ValueError, match="Username já existe"):
            service.create_user(data)
    
    def test_create_user_duplicate_email(self, session, sample_user):
        """Teste de criação com email duplicado"""
        service = UserService(session)
        data = {
            "username": "otheruser",
            "email": "test@example.com",  # Já existe
            "password": "Pass123"
        }
        
        with pytest.raises(ValueError, match="Email já existe"):
            service.create_user(data)
    
    def test_update_user(self, session, sample_user):
        """Teste de atualização de usuário"""
        service = UserService(session)
        data = {
            "username": "updateduser"
        }
        
        updated = service.update_user(sample_user.id, data)
        
        assert updated['username'] == "updateduser"
    
    def test_delete_user(self, session, sample_user):
        """Teste de remoção de usuário"""
        service = UserService(session)
        user_id = sample_user.id
        
        result = service.delete_user(user_id)
        
        assert result is True
        assert service.get_user_by_id(user_id) is None

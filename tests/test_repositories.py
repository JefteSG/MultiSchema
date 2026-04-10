"""
Testes para a camada de Repository (User)
"""
import pytest
from backend.repositories.user_repository import UserRepository
from backend.models.user import User
from backend.utils.auth import hash_password


class TestUserRepository:
    """Testes para UserRepository"""
    
    def test_find_all(self, session, sample_user):
        """Teste de busca de todos os usuários"""
        repo = UserRepository(session)
        users = repo.find_all()
        
        assert len(users) >= 1
        assert any(u.username == "testuser" for u in users)
    
    def test_find_by_id(self, session, sample_user):
        """Teste de busca por ID"""
        repo = UserRepository(session)
        user = repo.find_by_id(sample_user.id)
        
        assert user is not None
        assert user.id == sample_user.id
        assert user.username == "testuser"
    
    def test_find_by_username(self, session, sample_user):
        """Teste de busca por username"""
        repo = UserRepository(session)
        user = repo.find_by_username("testuser")
        
        assert user is not None
        assert user.username == "testuser"
    
    def test_find_by_email(self, session, sample_user):
        """Teste de busca por email"""
        repo = UserRepository(session)
        user = repo.find_by_email("test@example.com")
        
        assert user is not None
        assert user.email == "test@example.com"
    
    def test_create_user(self, session):
        """Teste de criação de usuário"""
        repo = UserRepository(session)
        new_user = User(
            username="newuser",
            email="new@example.com",
            password=hash_password("NewPass123")
        )
        
        created = repo.create(new_user)
        
        assert created.id is not None
        assert created.username == "newuser"
        assert created.email == "new@example.com"
    
    def test_exists_by_username(self, session, sample_user):
        """Teste de verificação de existência por username"""
        repo = UserRepository(session)
        
        assert repo.exists_by_username("testuser") is True
        assert repo.exists_by_username("nonexistent") is False
    
    def test_exists_by_email(self, session, sample_user):
        """Teste de verificação de existência por email"""
        repo = UserRepository(session)
        
        assert repo.exists_by_email("test@example.com") is True
        assert repo.exists_by_email("nonexistent@example.com") is False
    
    def test_update_user(self, session, sample_user):
        """Teste de atualização de usuário"""
        repo = UserRepository(session)
        
        sample_user.username = "updateduser"
        updated = repo.update(sample_user)
        
        assert updated.username == "updateduser"
    
    def test_delete_user(self, session):
        """Teste de remoção de usuário"""
        repo = UserRepository(session)
        
        user = User(
            username="deleteme",
            email="delete@example.com",
            password=hash_password("Pass123")
        )
        created = repo.create(user)
        user_id = created.id
        
        repo.delete(created)
        
        assert repo.find_by_id(user_id) is None

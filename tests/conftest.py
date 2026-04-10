"""
Configuração do pytest e fixtures compartilhadas
"""
import pytest
import os
import tempfile
from backend.app import create_app
from backend.database import db
from backend.models.user import User, Role


@pytest.fixture(scope='session')
def app():
    """Cria uma instância de teste da aplicação para toda a sessão"""
    # Criar banco temporário
    db_fd, db_path = tempfile.mkstemp()
    
    # Configurar app de teste
    app = create_app('testing')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['TESTING'] = True
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
    
    # Limpar
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Cliente de teste para fazer requisições HTTP"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Runner de comandos CLI"""
    return app.test_cli_runner()


@pytest.fixture
def session(app):
    """Sessão de banco de dados para testes"""
    with app.app_context():
        yield db.session
        db.session.rollback()


@pytest.fixture
def sample_user(session):
    """Cria um usuário de exemplo para testes"""
    from backend.utils.auth import hash_password
    
    user = User(
        username="testuser",
        email="test@example.com",
        password=hash_password("TestPass123")
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

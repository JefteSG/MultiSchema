"""
User Repository - Camada de acesso a dados para usuários
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from ..models.user import User, Role


class UserRepository:
    """Repository para operações de banco de dados de usuários"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def find_all(self) -> List[User]:
        """Retorna todos os usuários"""
        return self.session.query(User).all()
    
    def find_by_id(self, user_id: int) -> Optional[User]:
        """Busca usuário por ID"""
        return self.session.query(User).filter_by(id=user_id).first()
    
    def find_by_username(self, username: str) -> Optional[User]:
        """Busca usuário por username"""
        return self.session.query(User).filter_by(username=username).first()
    
    def find_by_email(self, email: str) -> Optional[User]:
        """Busca usuário por email"""
        return self.session.query(User).filter_by(email=email).first()
    
    def create(self, user: User) -> User:
        """Cria um novo usuário"""
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
    
    def update(self, user: User) -> User:
        """Atualiza um usuário existente"""
        self.session.commit()
        self.session.refresh(user)
        return user
    
    def delete(self, user: User) -> None:
        """Remove um usuário"""
        self.session.delete(user)
        self.session.commit()
    
    def exists_by_username(self, username: str) -> bool:
        """Verifica se username já existe"""
        return self.session.query(User).filter_by(username=username).first() is not None
    
    def exists_by_email(self, email: str) -> bool:
        """Verifica se email já existe"""
        return self.session.query(User).filter_by(email=email).first() is not None

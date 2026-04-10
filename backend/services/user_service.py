"""
User Service - Lógica de negócio para usuários
"""
import re
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from ..repositories.user_repository import UserRepository
from ..models.user import User
from ..utils.auth import hash_password, validate_password_strength


class UserService:
    """Service para lógica de negócio de usuários"""
    
    def __init__(self, session: Session):
        self.repository = UserRepository(session)
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Valida formato do email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_user_data(data: Dict, is_update: bool = False) -> List[str]:
        """Valida dados do usuário e retorna lista de erros"""
        errors = []
        
        # Validação de username
        if not is_update or 'username' in data:
            username = data.get('username', '').strip()
            if not username:
                errors.append("Username é obrigatório")
            elif len(username) < 3:
                errors.append("Username deve ter pelo menos 3 caracteres")
            elif len(username) > 50:
                errors.append("Username deve ter no máximo 50 caracteres")
        
        # Validação de email
        if not is_update or 'email' in data:
            email = data.get('email', '').strip()
            if not email:
                errors.append("Email é obrigatório")
            elif not UserService.validate_email(email):
                errors.append("Formato de email inválido")
        
        # Validação de senha
        if not is_update or 'password' in data:
            password = data.get('password', '')
            if not password:
                errors.append("Password é obrigatório")
            else:
                password_errors = validate_password_strength(password)
                errors.extend(password_errors)
        
        return errors
    
    def get_all_users(self) -> List[Dict]:
        """Retorna todos os usuários"""
        users = self.repository.find_all()
        return [user.to_dict() for user in users]
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Busca usuário por ID"""
        user = self.repository.find_by_id(user_id)
        return user.to_dict() if user else None
    
    def create_user(self, data: Dict) -> Dict:
        """
        Cria um novo usuário
        Retorna dicionário com sucesso ou levanta exceção
        """
        # Validar dados
        errors = self.validate_user_data(data)
        if errors:
            raise ValueError(f"Dados inválidos: {', '.join(errors)}")
        
        # Verificar duplicatas
        if self.repository.exists_by_username(data['username']):
            raise ValueError("Username já existe")
        
        if self.repository.exists_by_email(data['email']):
            raise ValueError("Email já existe")
        
        # Criar usuário
        new_user = User(
            username=data['username'].strip(),
            email=data['email'].strip().lower(),
            password=hash_password(data['password'])
        )
        
        created_user = self.repository.create(new_user)
        return created_user.to_dict()
    
    def update_user(self, user_id: int, data: Dict) -> Optional[Dict]:
        """Atualiza um usuário existente"""
        user = self.repository.find_by_id(user_id)
        if not user:
            raise ValueError("Usuário não encontrado")
        
        # Validar dados de atualização
        errors = self.validate_user_data(data, is_update=True)
        if errors:
            raise ValueError(f"Dados inválidos: {', '.join(errors)}")
        
        # Atualizar campos
        if 'username' in data:
            # Verificar se novo username já existe (e não é o mesmo usuário)
            existing = self.repository.find_by_username(data['username'])
            if existing and existing.id != user_id:
                raise ValueError("Username já existe")
            user.username = data['username'].strip()
        
        if 'email' in data:
            # Verificar se novo email já existe (e não é o mesmo usuário)
            existing = self.repository.find_by_email(data['email'])
            if existing and existing.id != user_id:
                raise ValueError("Email já existe")
            user.email = data['email'].strip().lower()
        
        if 'password' in data:
            user.password = hash_password(data['password'])
        
        updated_user = self.repository.update(user)
        return updated_user.to_dict()
    
    def delete_user(self, user_id: int) -> bool:
        """Remove um usuário"""
        user = self.repository.find_by_id(user_id)
        if not user:
            raise ValueError("Usuário não encontrado")
        
        self.repository.delete(user)
        return True

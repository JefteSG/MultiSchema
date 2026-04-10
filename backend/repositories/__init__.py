"""
Repositories - Camada de acesso a dados
Responsável por todas as operações de banco de dados (CRUD)
"""
from .user_repository import UserRepository
from .site_repository import SiteRepository

__all__ = ['UserRepository', 'SiteRepository']

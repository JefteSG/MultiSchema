"""
Site Service - Lógica de negócio para sites
"""
import os
from typing import List, Dict
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app
from ..repositories.site_repository import SiteRepository
from ..database import db


class SiteService:
    """Service para lógica de negócio de sites"""
    
    def __init__(self):
        self.repository = SiteRepository()
    
    @staticmethod
    def validate_site_name(site_name: str) -> List[str]:
        """Valida nome do site e retorna lista de erros"""
        errors = []
        
        if not site_name or len(site_name) < 3:
            errors.append("Nome do site deve ter pelo menos 3 caracteres")
        
        if not site_name.replace('_', '').replace('-', '').isalnum():
            errors.append("Nome do site deve conter apenas letras, números, - e _")
        
        return errors
    
    def get_all_sites(self) -> List[Dict]:
        """Retorna todos os sites"""
        return self.repository.find_all()
    
    def get_site_by_name(self, site_name: str) -> Dict:
        """Busca site por nome"""
        site = self.repository.find_by_name(site_name)
        if not site:
            raise ValueError("Site não encontrado")
        return site
    
    def create_site(self, data: Dict) -> Dict:
        """
        Cria um novo site com banco de dados isolado
        """
        site_name = data.get('site_name', '').strip()
        
        # Validar nome
        errors = self.validate_site_name(site_name)
        if errors:
            raise ValueError(f"Dados inválidos: {', '.join(errors)}")
        
        # Verificar se já existe
        if self.repository.exists(site_name):
            raise ValueError("Site já existe")
        
        # Criar diretório do site
        site_path = self.repository.create_directory(site_name)
        
        try:
            # Criar banco de dados SQLite
            db_path = self.repository.get_db_path(site_name)
            db_url = f"sqlite:///{db_path}"
            
            engine = create_engine(db_url)
            
            # Criar tabelas usando metadata do Flask-SQLAlchemy
            with current_app.app_context():
                db.metadata.create_all(engine)
            
            # Configuração do site
            site_config = {
                "site_name": site_name,
                "db_path": db_path,
                "db_url": db_url,
                "created_at": str(os.path.getctime(site_path)),
                "description": data.get('description', ''),
                "status": "active"
            }
            
            # Salvar configuração
            self.repository.save_config(site_name, site_config)
            
            return {
                "message": "Site criado com sucesso",
                "site_config": site_config
            }
            
        except SQLAlchemyError as e:
            # Rollback: remover pasta se criação falhou
            self.repository.delete(site_name)
            raise ValueError(f"Erro ao criar banco de dados: {str(e)}")
    
    def delete_site(self, site_name: str) -> bool:
        """Remove um site"""
        if not self.repository.exists(site_name):
            raise ValueError("Site não encontrado")
        
        self.repository.delete(site_name)
        return True

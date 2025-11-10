import os
import json
from typing import Optional


class Config:
    """Classe de configuração unificada para o MultiSchema"""
    
    # Configurações básicas
    DEBUG = os.environ.get('FLASK_ENV') == 'development'
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Configurações do SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = DEBUG
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }
    
    # Diretórios
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    INSTANCE_PATH = os.environ.get('INSTANCE_PATH', '/tmp/flask_instance')
    SITES_DIR = os.path.join(BASE_DIR, 'sites')
    
    @classmethod
    def get_database_url(cls) -> str:
        """
        Retorna a URL do banco de dados principal
        Ordem de precedência: 
        1. Variável de ambiente DATABASE_URL
        2. Arquivo de configuração sites/config.json
        3. SQLite padrão
        """
        # 1. Variável de ambiente
        database_url = os.environ.get('DATABASE_URL')
        if database_url:
            return database_url
        
        # 2. Arquivo de configuração
        try:
            config_path = os.path.join(cls.SITES_DIR, 'config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    if 'db_url' in config:
                        return config['db_url']
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        
        # 3. SQLite padrão
        os.makedirs(cls.INSTANCE_PATH, exist_ok=True)
        return f"sqlite:///{os.path.join(cls.INSTANCE_PATH, 'database.db')}"
    
    @classmethod
    def save_database_config(cls, db_url: str) -> None:
        """
        Salva a configuração do banco de dados no arquivo de configuração
        """
        os.makedirs(cls.SITES_DIR, exist_ok=True)
        config_path = os.path.join(cls.SITES_DIR, 'config.json')
        
        config = {}
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
            except json.JSONDecodeError:
                config = {}
        
        config['db_url'] = db_url
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
    
    @classmethod
    def get_site_database_url(cls, site_name: str) -> Optional[str]:
        """
        Retorna a URL do banco de dados específico de um site
        """
        site_dir = os.path.join(cls.SITES_DIR, site_name)
        config_path = os.path.join(site_dir, 'site_config.json')
        
        if not os.path.exists(config_path):
            return None
        
        try:
            with open(config_path, 'r') as f:
                site_config = json.load(f)
                return site_config.get('db_url')
        except (FileNotFoundError, json.JSONDecodeError):
            return None


class DevelopmentConfig(Config):
    """Configuração para desenvolvimento"""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Configuração para produção"""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    @classmethod
    def get_database_url(cls) -> str:
        """Em produção, exige DATABASE_URL"""
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL deve ser definida em produção")
        return database_url


class TestingConfig(Config):
    """Configuração para testes"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Mapeamento de configurações
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name: str = None) -> Config:
    """
    Retorna a classe de configuração baseada no nome ou ambiente
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    return config_by_name.get(config_name, DevelopmentConfig)
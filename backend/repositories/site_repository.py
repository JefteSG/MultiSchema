"""
Site Repository - Camada de acesso a dados para sites
"""
import os
import json
from typing import List, Dict, Optional
from ..config_manager import Config


class SiteRepository:
    """Repository para operações de arquivos e configurações de sites"""
    
    def __init__(self, sites_dir: str = None):
        self.sites_dir = sites_dir or Config.SITES_DIR
    
    def find_all(self) -> List[Dict]:
        """Retorna todos os sites com suas configurações"""
        if not os.path.exists(self.sites_dir):
            return []
        
        sites = []
        for item in os.listdir(self.sites_dir):
            site_path = os.path.join(self.sites_dir, item)
            if os.path.isdir(site_path) and item != '__pycache__':
                config_path = os.path.join(site_path, 'site_config.json')
                if os.path.exists(config_path):
                    try:
                        with open(config_path, 'r') as f:
                            site_config = json.load(f)
                            sites.append({
                                "name": item,
                                "config": site_config
                            })
                    except json.JSONDecodeError:
                        continue
        
        return sites
    
    def find_by_name(self, site_name: str) -> Optional[Dict]:
        """Busca site por nome"""
        site_path = os.path.join(self.sites_dir, site_name)
        if not os.path.exists(site_path):
            return None
        
        config_path = os.path.join(site_path, 'site_config.json')
        if not os.path.exists(config_path):
            return None
        
        try:
            with open(config_path, 'r') as f:
                site_config = json.load(f)
                return {
                    "name": site_name,
                    "config": site_config
                }
        except json.JSONDecodeError:
            return None
    
    def exists(self, site_name: str) -> bool:
        """Verifica se um site existe"""
        site_path = os.path.join(self.sites_dir, site_name)
        return os.path.exists(site_path)
    
    def create_directory(self, site_name: str) -> str:
        """Cria o diretório do site e retorna o caminho"""
        site_path = os.path.join(self.sites_dir, site_name)
        os.makedirs(site_path, exist_ok=True)
        return site_path
    
    def save_config(self, site_name: str, config: Dict) -> None:
        """Salva a configuração do site"""
        site_path = os.path.join(self.sites_dir, site_name)
        config_path = os.path.join(site_path, 'site_config.json')
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
    
    def delete(self, site_name: str) -> None:
        """Remove um site e todos seus arquivos"""
        import shutil
        site_path = os.path.join(self.sites_dir, site_name)
        if os.path.exists(site_path):
            shutil.rmtree(site_path)
    
    def get_db_path(self, site_name: str) -> str:
        """Retorna o caminho do banco de dados do site"""
        site_path = os.path.join(self.sites_dir, site_name)
        return os.path.join(site_path, "database.db")

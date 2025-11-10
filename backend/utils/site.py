import os
import json
from flask import request, abort


def get_base_path():
    # retorna o caminho do backend
    return os.path.join(os.path.dirname(os.path.abspath('.')), 'backend')


def get_list_sites():
    sites_dir = os.path.join(get_base_path(), 'sites')
    print(f"Checking if {sites_dir} exists: {os.path.exists(sites_dir)}")
    if not os.path.exists(sites_dir):
        return []
    sites = [f for f in os.listdir(sites_dir) if os.path.isdir(os.path.join(sites_dir, f))]
    return sites


def get_exists_site(site_name):
    return site_name in get_list_sites()


def get_db_url(site_name):
    try:
        if site_name not in get_list_sites():
            abort(404, description=f"Site '{site_name}' não encontrado")
        
        sites_dir = os.path.join(get_base_path(), 'sites')
        site_dir = os.path.join(sites_dir, site_name)
        site_config_path = os.path.join(site_dir, 'site_config.json')
        
        if not os.path.exists(site_config_path):
            abort(500, description=f"Arquivo de configuração não encontrado para o site '{site_name}'")
        
        with open(site_config_path, 'r') as f:
            site_config = json.load(f)
        
        if 'db_url' not in site_config:
            abort(500, description=f"URL do banco de dados não configurada para o site '{site_name}'")
            
        return site_config['db_url']
    
    except FileNotFoundError:
        abort(500, description=f"Erro ao acessar configurações do site '{site_name}'")
    except json.JSONDecodeError:
        abort(500, description=f"Arquivo de configuração corrompido para o site '{site_name}'")
    except Exception as e:
        abort(500, description=f"Erro inesperado ao buscar URL do banco de dados: {str(e)}")


def get_config_db_root():
    try:
        sites_dir = os.path.join(get_base_path(), 'sites')
        config_path = os.path.join(sites_dir, 'config.json')
        
        if not os.path.exists(config_path):
            abort(500, description='Arquivo de configuração principal não encontrado. Execute "flask init" para configurar o banco de dados.')
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if 'db_url' not in config:
            abort(500, description='Configuração do banco de dados não encontrada. Execute "flask init" para configurar o banco de dados.')
        
        return config.get('db_url')
    
    except FileNotFoundError:
        abort(500, description='Erro ao acessar arquivo de configuração principal.')
    except json.JSONDecodeError:
        abort(500, description='Arquivo de configuração principal corrompido.')
    except Exception as e:
        abort(500, description=f'Erro inesperado ao buscar configuração do banco: {str(e)}')
import os
import json
from flask import request

def get_base_path():
    # retorna o caminho do backend
    return os.path.join(os.path.dirname(os.path.abspath('.')), 'backend')


def get_list_sites():
    sites_dir = os.path.join(get_base_path(), 'sites')
    sites = [f for f in os.listdir(sites_dir) if os.path.isdir(os.path.join(sites_dir, f))]
    return sites

def get_exists_site(site_name):
    return site_name in get_list_sites()

def get_db_url(site_name):
    try:
        if site_name not in get_list_sites():
            request.abort(404)
        sites_dir = os.path.join(get_base_path(), 'sites')
        site_dir = os.path.join(sites_dir, site_name)
        site_config_path = os.path.join(site_dir, 'site_config.json')
        with open(site_config_path, 'r') as f:
            site_config = json.load(f)
        return site_config['db_url']
    except Exception as e:
        request.abort(500, f"Erro ao buscar URL do banco de dados: {str(e)}")

def get_config_db_root():
    sites_dir = os.path.join(get_base_path(), 'sites')
    config_path = os.path.join(sites_dir, 'config.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    if 'db_url' not in config:
        request.abort(500, 'Erro ao buscar configuração do banco de dados, voce deve configurar o banco com o comando "flask init"')
    return config.get('db_url')
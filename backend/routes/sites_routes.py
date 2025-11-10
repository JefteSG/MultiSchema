import os
import json
import secrets
import click
from flask import Blueprint, request, jsonify, g, current_app
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from ..database import db
from ..config_manager import Config

sites_bp = Blueprint("sites", __name__, url_prefix='/api/v1/sites')


@sites_bp.route('/', methods=['GET'])
def list_sites():
    """Lista todos os sites disponíveis"""
    try:
        sites_dir = Config.SITES_DIR
        if not os.path.exists(sites_dir):
            return jsonify({"sites": []}), 200
        
        sites = []
        for item in os.listdir(sites_dir):
            site_path = os.path.join(sites_dir, item)
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
                        # Ignora sites com configuração corrompida
                        continue
        
        return jsonify({"sites": sites}), 200
    
    except Exception as e:
        return jsonify({"error": f"Erro ao listar sites: {str(e)}"}), 500


@sites_bp.route('/', methods=['POST'])
def create_site():
    """
    Cria um novo site com um banco de dados exclusivo usando SQLite.
    """
    try:
        data = request.get_json()
        if not data or 'site_name' not in data:
            return jsonify({'error': 'Nome do site é obrigatório'}), 400
        
        site_name = data['site_name'].strip()
        
        # Validar nome do site
        if not site_name or len(site_name) < 3:
            return jsonify({'error': 'Nome do site deve ter pelo menos 3 caracteres'}), 400
        
        if not site_name.replace('_', '').replace('-', '').isalnum():
            return jsonify({'error': 'Nome do site deve conter apenas letras, números, - e _'}), 400
        
        # Verificar se site já existe
        site_folder = os.path.join(Config.SITES_DIR, site_name)
        if os.path.exists(site_folder):
            return jsonify({'error': 'Site já existe'}), 409
        
        # Criar pasta do site
        os.makedirs(site_folder, exist_ok=True)

        # Definir caminho do banco SQLite
        new_db_path = os.path.join(site_folder, "database.db")
        new_db_url = f"sqlite:///{new_db_path}"

        try:
            # Criar o banco de dados SQLite
            engine_new = create_engine(new_db_url)
            
            # Criar tabelas usando metadata do Flask-SQLAlchemy
            with current_app.app_context():
                db.metadata.create_all(engine_new)
            
        except SQLAlchemyError as e:
            # Remover pasta se criação falhou
            if os.path.exists(site_folder):
                import shutil
                shutil.rmtree(site_folder)
            return jsonify({"error": f"Erro ao criar banco de dados: {str(e)}"}), 500

        # Configuração do site
        site_config = {
            "site_name": site_name,
            "db_path": new_db_path,
            "db_url": new_db_url,
            "created_at": str(os.path.getctime(site_folder)),
            "description": data.get('description', ''),
            "status": "active"
        }

        try:
            # Salvar configurações em arquivo JSON
            config_path = os.path.join(site_folder, "site_config.json")
            with open(config_path, "w") as config_file:
                json.dump(site_config, config_file, indent=4)
        except Exception as e:
            # Remover pasta se salvamento falhou
            if os.path.exists(site_folder):
                import shutil
                shutil.rmtree(site_folder)
            return jsonify({"error": f"Erro ao salvar configuração: {str(e)}"}), 500

        return jsonify({
            "message": f"Site '{site_name}' criado com sucesso!",
            "site_config": site_config
        }), 201
    
    except Exception as e:
        return jsonify({"error": f"Erro inesperado: {str(e)}"}), 500


@sites_bp.route('/<site_name>', methods=['GET'])
def get_site(site_name):
    """Obtém informações de um site específico"""
    try:
        site_folder = os.path.join(Config.SITES_DIR, site_name)
        config_path = os.path.join(site_folder, "site_config.json")
        
        if not os.path.exists(config_path):
            return jsonify({'error': 'Site não encontrado'}), 404
        
        with open(config_path, 'r') as f:
            site_config = json.load(f)
        
        return jsonify(site_config), 200
    
    except json.JSONDecodeError:
        return jsonify({'error': 'Configuração do site corrompida'}), 500
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar site: {str(e)}'}), 500


@sites_bp.route('/<site_name>', methods=['DELETE'])
def delete_site(site_name):
    """Remove um site e todos os seus dados"""
    try:
        site_folder = os.path.join(Config.SITES_DIR, site_name)
        
        if not os.path.exists(site_folder):
            return jsonify({'error': 'Site não encontrado'}), 404
        
        # Remover pasta do site completamente
        import shutil
        shutil.rmtree(site_folder)
        
        return jsonify({'message': f"Site '{site_name}' removido com sucesso"}), 200
    
    except Exception as e:
        return jsonify({'error': f'Erro ao remover site: {str(e)}'}), 500
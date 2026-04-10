import os
import json
from flask import Blueprint, request, jsonify
from ..services.site_service import SiteService

sites_bp = Blueprint("sites", __name__, url_prefix='/api/v1/sites')


@sites_bp.route('/', methods=['GET'])
def list_sites():
    """Lista todos os sites disponíveis"""
    try:
        service = SiteService()
        sites = service.get_all_sites()
        return jsonify({"sites": sites}), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao listar sites: {str(e)}"}), 500


@sites_bp.route('/', methods=['POST'])
def create_site():
    """Cria um novo site com banco de dados isolado"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        service = SiteService()
        result = service.create_site(data)
        
        return jsonify(result), 201
    except ValueError as e:
        # Erros de validação ou duplicação
        error_msg = str(e)
        if "já existe" in error_msg:
            return jsonify({'error': error_msg}), 409
        return jsonify({'error': error_msg}), 400
    except Exception as e:
        return jsonify({"error": f"Erro ao criar site: {str(e)}"}), 500


@sites_bp.route('/<site_name>', methods=['GET'])
def get_site(site_name):
    """Obtém informações de um site específico"""
    try:
        service = SiteService()
        site = service.get_site_by_name(site_name)
        return jsonify(site['config']), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar site: {str(e)}'}), 500


@sites_bp.route('/<site_name>', methods=['DELETE'])
def delete_site(site_name):
    """Remove um site e todos os seus dados"""
    try:
        service = SiteService()
        service.delete_site(site_name)
        return jsonify({'message': f"Site '{site_name}' removido com sucesso"}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'Erro ao remover site: {str(e)}'}), 500
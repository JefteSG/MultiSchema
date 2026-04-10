from flask import Blueprint, request, jsonify, g
from ..services.user_service import UserService

user_bp = Blueprint("user", __name__, url_prefix='/api/v1/user')


@user_bp.route('/', methods=['GET'])
def get_list_users():
    """Lista todos os usuários"""
    try:
        service = UserService(g.db_session)
        users = service.get_all_users()
        return jsonify(users), 200
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar usuários: {str(e)}'}), 500


@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Busca um usuário por ID"""
    try:
        service = UserService(g.db_session)
        user = service.get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        return jsonify(user), 200
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar usuário: {str(e)}'}), 500


@user_bp.route('/', methods=['POST'])
def create_user():
    """Cria um novo usuário"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        service = UserService(g.db_session)
        user = service.create_user(data)
        
        return jsonify(user), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Erro ao criar usuário: {str(e)}'}), 500


@user_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Atualiza um usuário existente"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        service = UserService(g.db_session)
        user = service.update_user(user_id, data)
        
        return jsonify(user), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Erro ao atualizar usuário: {str(e)}'}), 500


@user_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Remove um usuário"""
    try:
        service = UserService(g.db_session)
        service.delete_user(user_id)
        
        return jsonify({'message': 'Usuário removido com sucesso'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'Erro ao remover usuário: {str(e)}'}), 500
from flask import Blueprint, request, jsonify, g
from ..models.user import User 
from ..utils.auth import hash_password, validate_password_strength
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
import re

user_bp = Blueprint("user", __name__, url_prefix='/api/v1/user')


def validate_email(email):
    """Valida formato do email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_user_data(data, is_update=False):
    """Valida dados do usuário"""
    errors = []
    
    if not is_update or 'username' in data:
        username = data.get('username', '').strip()
        if not username:
            errors.append("Username é obrigatório")
        elif len(username) < 3:
            errors.append("Username deve ter pelo menos 3 caracteres")
        elif len(username) > 50:
            errors.append("Username deve ter no máximo 50 caracteres")
    
    if not is_update or 'email' in data:
        email = data.get('email', '').strip()
        if not email:
            errors.append("Email é obrigatório")
        elif not validate_email(email):
            errors.append("Formato de email inválido")
    
    if not is_update or 'password' in data:
        password = data.get('password', '')
        if not password:
            errors.append("Password é obrigatório")
        else:
            # Validar força da senha
            password_errors = validate_password_strength(password)
            errors.extend(password_errors)
    
    return errors


@user_bp.route('/', methods=['GET'])
def get_list_users():
    try:
        session = g.db_session
        Users = session.query(User).all()
        return jsonify([user.to_dict() for user in Users]), 200
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar usuários: {str(e)}'}), 500


@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        session = g.db_session
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        return jsonify(user.to_dict()), 200
    except Exception as e:
        return jsonify({'error': f'Erro ao buscar usuário: {str(e)}'}), 500


@user_bp.route('/', methods=['POST'])
def create_user():
    try:
        session = g.db_session
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400

        # Validar dados
        errors = validate_user_data(data)
        if errors:
            return jsonify({'error': 'Dados inválidos', 'details': errors}), 400

        # Verificar se username já existe
        existing_user = session.query(User).filter_by(username=data['username']).first()
        if existing_user:
            return jsonify({'error': 'Username já existe'}), 409

        # Verificar se email já existe
        existing_email = session.query(User).filter_by(email=data['email']).first()
        if existing_email:
            return jsonify({'error': 'Email já existe'}), 409

        new_user = User(
            username=data['username'].strip(),
            email=data['email'].strip().lower(),
            password=hash_password(data['password'])
        )

        session.add(new_user)
        session.commit()

        return jsonify(new_user.to_dict()), 201
    
    except IntegrityError as e:
        session.rollback()
        return jsonify({'error': 'Erro de integridade dos dados'}), 409
    except Exception as e:
        session.rollback()
        return jsonify({'error': f'Erro ao criar usuário: {str(e)}'}), 500


@user_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        session = g.db_session
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400

        # Validar dados
        errors = validate_user_data(data, is_update=True)
        if errors:
            return jsonify({'error': 'Dados inválidos', 'details': errors}), 400

        # Verificar conflitos apenas se os dados foram alterados
        if 'username' in data and data['username'] != user.username:
            existing_user = session.query(User).filter_by(username=data['username']).first()
            if existing_user:
                return jsonify({'error': 'Username já existe'}), 409

        if 'email' in data and data['email'] != user.email:
            existing_email = session.query(User).filter_by(email=data['email']).first()
            if existing_email:
                return jsonify({'error': 'Email já existe'}), 409

        # Atualizar campos
        if 'username' in data:
            user.username = data['username'].strip()
        if 'email' in data:
            user.email = data['email'].strip().lower()
        if 'password' in data:
            user.password = hash_password(data['password'])

        session.commit()

        return jsonify(user.to_dict()), 200
    
    except IntegrityError as e:
        session.rollback()
        return jsonify({'error': 'Erro de integridade dos dados'}), 409
    except Exception as e:
        session.rollback()
        return jsonify({'error': f'Erro ao atualizar usuário: {str(e)}'}), 500


@user_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        session = g.db_session
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404

        session.delete(user)
        session.commit()

        return jsonify({'message': 'Usuário removido com sucesso'}), 200
    
    except Exception as e:
        session.rollback()
        return jsonify({'error': f'Erro ao remover usuário: {str(e)}'}), 500
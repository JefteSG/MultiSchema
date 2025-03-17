from flask import Blueprint, request, jsonify, g
from ..models.user import User 
from sqlalchemy.orm import joinedload

user_bp = Blueprint("user", __name__, url_prefix='/api/v1/user')


@user_bp.route('/', methods=['GET'])
def get_list_users():
    session = g.db_session
    Users = session.query(User).all()
    return jsonify([user.to_dict() for user in Users]), 200

@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    session = g.db_session
    user = session.query(User).filter_by(id=user_id).first()
    return jsonify(user.to_dict()), 200

@user_bp.route('/', methods=['POST'])
def create_user():
    session = g.db_session
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data provided'}), 400

    new_user = User(
        username=data['username'],
        email=data['email'],
        password=data['password']
    )

    session.add(new_user)
    session.commit()

    return jsonify(new_user.to_dict()), 201

@user_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    session = g.db_session
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data provided'}), 400

    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    user.password = data.get('password', user.password)

    session.commit()

    return jsonify(user.to_dict()), 200

@user_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    session = g.db_session
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    session.delete(user)
    session.commit()

    return jsonify({'message': 'User deleted successfully'}), 200
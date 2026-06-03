import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.extensions import db
from app.models.user import User, Role, Permission
from app.utils.auth import admin_required

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({'error': '用户名或密码错误'}), 401

    if not user.is_active:
        return jsonify({'error': '账号已被禁用'}), 403

    access_token = create_access_token(identity=str(user.id), additional_claims={
        'username': user.username,
        'roles': [r.code for r in user.roles]
    })

    return jsonify({
        'access_token': access_token,
        'user': user.to_dict()
    })

@auth_bp.route('/register', methods=['POST'])
@admin_required
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'error': '缺少必要参数'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': '用户名已存在'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': '邮箱已被使用'}), 400

    user = User(username=username, email=email, real_name=data.get('real_name'))
    user.set_password(password)

    role_code = data.get('role')
    if role_code:
        role = Role.query.filter_by(code=role_code).first()
        if role:
            user.roles.append(role)

    db.session.add(user)
    db.session.commit()

    return jsonify({'message': '注册成功', 'user': user.to_dict()}), 201

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    return jsonify(user.to_dict())

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    data = request.get_json()

    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not user.check_password(old_password):
        return jsonify({'error': '原密码错误'}), 400

    user.set_password(new_password)
    db.session.commit()

    return jsonify({'message': '密码修改成功'})

@auth_bp.route('/init-password', methods=['POST'])
@admin_required
def init_password():
    data = request.get_json()
    user_id = data.get('user_id')
    new_password = data.get('new_password')

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404

    user.set_password(new_password)
    db.session.commit()

    return jsonify({'message': '密码重置成功'})
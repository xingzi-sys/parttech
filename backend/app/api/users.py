from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.user import User, Role, Permission
from app.utils.auth import admin_required, manager_required
from app.utils.validators import sanitize_input

users_bp = Blueprint('users', __name__, url_prefix='/api/users')

@users_bp.route('', methods=['GET'])
@jwt_required()
def list_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    is_active = request.args.get('is_active')

    query = User.query

    if search:
        query = query.filter(User.username.contains(search) | User.real_name.contains(search) | User.email.contains(search))
    if is_active is not None:
        query = query.filter(User.is_active == (is_active == 'true'))

    query = query.order_by(User.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'items': [u.to_dict() for u in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

@users_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    return jsonify(user.to_dict())

@users_bp.route('', methods=['POST'])
@admin_required
def create_user():
    data = request.get_json()

    if not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': '缺少必要参数'}), 400

    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({'error': '用户名已存在'}), 400

    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({'error': '邮箱已被使用'}), 400

    user = User(
        username=sanitize_input(data.get('username')),
        email=data.get('email'),
        real_name=data.get('real_name'),
        department=data.get('department'),
        position=data.get('position'),
        is_active=data.get('is_active', True)
    )
    user.set_password(data.get('password'))

    role_codes = data.get('roles', [])
    for code in role_codes:
        role = Role.query.filter_by(code=code).first()
        if role:
            user.roles.append(role)

    db.session.add(user)
    db.session.commit()

    return jsonify(user.to_dict()), 201

@users_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_user(id):
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)

    user = User.query.get(id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404

    if not current_user.has_role('admin') and current_user_id != id:
        return jsonify({'error': '权限不足'}), 403

    data = request.get_json()

    if data.get('real_name') is not None:
        user.real_name = data.get('real_name')
    if data.get('department') is not None:
        user.department = data.get('department')
    if data.get('position') is not None:
        user.position = data.get('position')
    if current_user.has_role('admin'):
        if data.get('is_active') is not None:
            user.is_active = data.get('is_active')
        if data.get('roles'):
            user.roles = []
            for code in data.get('roles'):
                role = Role.query.filter_by(code=code).first()
                if role:
                    user.roles.append(role)
        if data.get('password'):
            user.set_password(data.get('password'))

    db.session.commit()

    return jsonify(user.to_dict())

@users_bp.route('/<int:id>', methods=['DELETE'])
@admin_required
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    if user.username == 'admin':
        return jsonify({'error': '不能删除超级管理员'}), 400

    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': '用户已删除'})

@users_bp.route('/roles', methods=['GET'])
@jwt_required()
def get_roles():
    roles = Role.query.all()
    return jsonify([r.to_dict() for r in roles])

@users_bp.route('/permissions', methods=['GET'])
@jwt_required()
def get_permissions():
    perms = Permission.query.all()
    return jsonify([p.to_dict() for p in perms])

@users_bp.route('/options', methods=['GET'])
@jwt_required()
def get_user_options():
    users = User.query.filter_by(is_active=True).all()
    return jsonify([{'id': u.id, 'name': u.real_name or u.username, 'department': u.department} for u in users])
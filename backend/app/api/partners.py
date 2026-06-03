import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.partner import Partner
from app.models.user import User
from app.utils.auth import admin_required, manager_required
from app.utils.validators import sanitize_input

partners_bp = Blueprint('partners', __name__, url_prefix='/api/partners')

@partners_bp.route('', methods=['GET'])
@jwt_required()
def list_partners():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    type_filter = request.args.get('type', '')
    level_filter = request.args.get('level', '')
    status_filter = request.args.get('status', '')

    query = Partner.query

    if search:
        query = query.filter(Partner.name.contains(search))
    if type_filter:
        query = query.filter(Partner.type == type_filter)
    if level_filter:
        query = query.filter(Partner.level == level_filter)
    if status_filter:
        query = query.filter(Partner.status == status_filter)

    query = query.order_by(Partner.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'items': [p.to_dict() for p in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

@partners_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_partner(id):
    partner = Partner.query.get(id)
    if not partner:
        return jsonify({'error': '合作商不存在'}), 404
    return jsonify(partner.to_dict())

@partners_bp.route('', methods=['POST'])
@jwt_required()
def create_partner():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data.get('name'):
        return jsonify({'error': '企业名称不能为空'}), 400

    partner = Partner(
        name=sanitize_input(data.get('name')),
        type=data.get('type'),
        credit_code=data.get('credit_code'),
        registered_address=data.get('registered_address'),
        website=data.get('website'),
        level=data.get('level', '普通'),
        status=data.get('status', '活跃'),
        tags=data.get('tags'),
        description=data.get('description'),
        created_by=user_id
    )

    db.session.add(partner)
    db.session.commit()

    return jsonify(partner.to_dict()), 201

@partners_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_partner(id):
    partner = Partner.query.get(id)
    if not partner:
        return jsonify({'error': '合作商不存在'}), 404

    data = request.get_json()

    if data.get('name'):
        partner.name = sanitize_input(data.get('name'))
    if data.get('type') is not None:
        partner.type = data.get('type')
    if data.get('credit_code') is not None:
        partner.credit_code = data.get('credit_code')
    if data.get('registered_address') is not None:
        partner.registered_address = data.get('registered_address')
    if data.get('website') is not None:
        partner.website = data.get('website')
    if data.get('level') is not None:
        partner.level = data.get('level')
    if data.get('status') is not None:
        partner.status = data.get('status')
    if data.get('tags') is not None:
        partner.tags = data.get('tags')
    if data.get('description') is not None:
        partner.description = data.get('description')

    db.session.commit()

    return jsonify(partner.to_dict())

@partners_bp.route('/<int:id>', methods=['DELETE'])
@manager_required
def delete_partner(id):
    partner = Partner.query.get(id)
    if not partner:
        return jsonify({'error': '合作商不存在'}), 404

    db.session.delete(partner)
    db.session.commit()

    return jsonify({'message': '删除成功'})

@partners_bp.route('/options', methods=['GET'])
@jwt_required()
def get_partner_options():
    partners = Partner.query.filter(Partner.status == '活跃').order_by(Partner.name).all()
    return jsonify([{'id': p.id, 'name': p.name, 'level': p.level} for p in partners])

@partners_bp.route('/types', methods=['GET'])
@jwt_required()
def get_partner_types():
    return jsonify(Partner.TYPE_CHOICES)

@partners_bp.route('/levels', methods=['GET'])
@jwt_required()
def get_partner_levels():
    return jsonify(Partner.LEVEL_CHOICES)

@partners_bp.route('/statuses', methods=['GET'])
@jwt_required()
def get_partner_statuses():
    return jsonify(Partner.STATUS_CHOICES)
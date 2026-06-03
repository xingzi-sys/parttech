from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.contact import Contact
from app.models.partner import Partner
from app.utils.validators import sanitize_input

contacts_bp = Blueprint('contacts', __name__, url_prefix='/api/contacts')

@contacts_bp.route('', methods=['GET'])
@jwt_required()
def list_contacts():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    partner_id = request.args.get('partner_id', type=int)

    query = Contact.query

    if partner_id:
        query = query.filter(Contact.partner_id == partner_id)

    query = query.order_by(Contact.is_primary.desc(), Contact.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'items': [c.to_dict() for c in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

@contacts_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_contact(id):
    contact = Contact.query.get(id)
    if not contact:
        return jsonify({'error': '联系人不存在'}), 404
    return jsonify(contact.to_dict())

@contacts_bp.route('', methods=['POST'])
@jwt_required()
def create_contact():
    data = request.get_json()

    if not data.get('partner_id'):
        return jsonify({'error': '必须关联合作商'}), 400
    if not data.get('name'):
        return jsonify({'error': '联系人姓名不能为空'}), 400

    partner = Partner.query.get(data.get('partner_id'))
    if not partner:
        return jsonify({'error': '合作商不存在'}), 404

    if data.get('is_primary'):
        Contact.query.filter_by(partner_id=data.get('partner_id'), is_primary=True).update({'is_primary': False})

    contact = Contact(
        partner_id=data.get('partner_id'),
        name=sanitize_input(data.get('name')),
        position=data.get('position'),
        role=data.get('role'),
        phone=data.get('phone'),
        email=data.get('email'),
        wechat=data.get('wechat'),
        is_primary=data.get('is_primary', False),
        notes=data.get('notes')
    )

    db.session.add(contact)
    db.session.commit()

    return jsonify(contact.to_dict()), 201

@contacts_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_contact(id):
    contact = Contact.query.get(id)
    if not contact:
        return jsonify({'error': '联系人不存在'}), 404

    data = request.get_json()

    if data.get('is_primary') and not contact.is_primary:
        Contact.query.filter_by(partner_id=contact.partner_id, is_primary=True).update({'is_primary': False})

    if data.get('name'):
        contact.name = sanitize_input(data.get('name'))
    if data.get('position') is not None:
        contact.position = data.get('position')
    if data.get('role') is not None:
        contact.role = data.get('role')
    if data.get('phone') is not None:
        contact.phone = data.get('phone')
    if data.get('email') is not None:
        contact.email = data.get('email')
    if data.get('wechat') is not None:
        contact.wechat = data.get('wechat')
    if data.get('is_primary') is not None:
        contact.is_primary = data.get('is_primary')
    if data.get('notes') is not None:
        contact.notes = data.get('notes')

    db.session.commit()

    return jsonify(contact.to_dict())

@contacts_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_contact(id):
    contact = Contact.query.get(id)
    if not contact:
        return jsonify({'error': '联系人不存在'}), 404

    db.session.delete(contact)
    db.session.commit()

    return jsonify({'message': '删除成功'})

@contacts_bp.route('/roles', methods=['GET'])
@jwt_required()
def get_contact_roles():
    return jsonify(Contact.ROLE_CHOICES)
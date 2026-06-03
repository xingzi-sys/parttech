from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.business_term import BusinessTerm
from app.models.partner import Partner
from app.models.product import Product

business_terms_bp = Blueprint('business_terms', __name__, url_prefix='/api/business-terms')

@business_terms_bp.route('', methods=['GET'])
@jwt_required()
def list_business_terms():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    partner_id = request.args.get('partner_id', type=int)
    product_id = request.args.get('product_id', type=int)
    term_type = request.args.get('term_type', '')
    status = request.args.get('status', '')

    query = BusinessTerm.query

    if partner_id:
        query = query.filter(BusinessTerm.partner_id == partner_id)
    if product_id:
        query = query.filter(BusinessTerm.product_id == product_id)
    if term_type:
        query = query.filter(BusinessTerm.term_type == term_type)
    if status:
        query = query.filter(BusinessTerm.status == status)

    query = query.order_by(BusinessTerm.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'items': [b.to_dict() for b in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

@business_terms_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_business_term(id):
    term = BusinessTerm.query.get(id)
    if not term:
        return jsonify({'error': '商务条件不存在'}), 404
    return jsonify(term.to_dict())

@business_terms_bp.route('', methods=['POST'])
@jwt_required()
def create_business_term():
    data = request.get_json()

    if not data.get('partner_id'):
        return jsonify({'error': '必须关联合作商'}), 400
    if not data.get('term_type'):
        return jsonify({'error': '条件类型不能为空'}), 400

    partner = Partner.query.get(data.get('partner_id'))
    if not partner:
        return jsonify({'error': '合作商不存在'}), 404

    term = BusinessTerm(
        partner_id=data.get('partner_id'),
        product_id=data.get('product_id'),
        term_type=data.get('term_type'),
        description=data.get('description'),
        valid_from=datetime.strptime(data['valid_from'], '%Y-%m-%d').date() if data.get('valid_from') else None,
        valid_until=datetime.strptime(data['valid_until'], '%Y-%m-%d').date() if data.get('valid_until') else None,
        status=data.get('status', '生效中')
    )

    db.session.add(term)
    db.session.commit()

    return jsonify(term.to_dict()), 201

@business_terms_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_business_term(id):
    term = BusinessTerm.query.get(id)
    if not term:
        return jsonify({'error': '商务条件不存在'}), 404

    data = request.get_json()

    if data.get('product_id') is not None:
        term.product_id = data.get('product_id')
    if data.get('term_type') is not None:
        term.term_type = data.get('term_type')
    if data.get('description') is not None:
        term.description = data.get('description')
    if data.get('valid_from') is not None:
        term.valid_from = datetime.strptime(data['valid_from'], '%Y-%m-%d').date() if data.get('valid_from') else None
    if data.get('valid_until') is not None:
        term.valid_until = datetime.strptime(data['valid_until'], '%Y-%m-%d').date() if data.get('valid_until') else None
    if data.get('status') is not None:
        term.status = data.get('status')

    db.session.commit()

    return jsonify(term.to_dict())

@business_terms_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_business_term(id):
    term = BusinessTerm.query.get(id)
    if not term:
        return jsonify({'error': '商务条件不存在'}), 404

    db.session.delete(term)
    db.session.commit()

    return jsonify({'message': '删除成功'})

@business_terms_bp.route('/types', methods=['GET'])
@jwt_required()
def get_term_types():
    return jsonify(BusinessTerm.TYPE_CHOICES)

@business_terms_bp.route('/statuses', methods=['GET'])
@jwt_required()
def get_term_statuses():
    return jsonify(BusinessTerm.STATUS_CHOICES)
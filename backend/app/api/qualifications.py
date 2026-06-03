from datetime import datetime, date
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.qualification import Qualification
from app.models.partner import Partner

qualifications_bp = Blueprint('qualifications', __name__, url_prefix='/api/qualifications')

@qualifications_bp.route('', methods=['GET'])
@jwt_required()
def list_qualifications():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    partner_id = request.args.get('partner_id', type=int)
    name = request.args.get('name', '')
    status = request.args.get('status', '')

    query = Qualification.query

    if partner_id:
        query = query.filter(Qualification.partner_id == partner_id)
    if name:
        query = query.filter(Qualification.name == name)
    if status:
        query = query.filter(Qualification.status == status)

    query = query.order_by(Qualification.valid_until.asc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'items': [q.to_dict() for q in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

@qualifications_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_qualification(id):
    qual = Qualification.query.get(id)
    if not qual:
        return jsonify({'error': '资质不存在'}), 404
    return jsonify(qual.to_dict())

@qualifications_bp.route('', methods=['POST'])
@jwt_required()
def create_qualification():
    data = request.get_json()

    if not data.get('partner_id'):
        return jsonify({'error': '必须关联合作商'}), 400
    if not data.get('name'):
        return jsonify({'error': '资质名称不能为空'}), 400

    partner = Partner.query.get(data.get('partner_id'))
    if not partner:
        return jsonify({'error': '合作商不存在'}), 404

    qual = Qualification(
        partner_id=data.get('partner_id'),
        name=data.get('name'),
        cert_no=data.get('cert_no'),
        issuer=data.get('issuer'),
        issue_date=datetime.strptime(data['issue_date'], '%Y-%m-%d').date() if data.get('issue_date') else None,
        valid_until=datetime.strptime(data['valid_until'], '%Y-%m-%d').date() if data.get('valid_until') else None,
        notes=data.get('notes')
    )

    if qual.valid_until:
        days_until = (qual.valid_until - date.today()).days
        if days_until < 0:
            qual.status = '已过期'
        elif days_until <= 30:
            qual.status = '即将到期'
        else:
            qual.status = '有效'

    db.session.add(qual)
    db.session.commit()

    return jsonify(qual.to_dict()), 201

@qualifications_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_qualification(id):
    qual = Qualification.query.get(id)
    if not qual:
        return jsonify({'error': '资质不存在'}), 404

    data = request.get_json()

    if data.get('name') is not None:
        qual.name = data.get('name')
    if data.get('cert_no') is not None:
        qual.cert_no = data.get('cert_no')
    if data.get('issuer') is not None:
        qual.issuer = data.get('issuer')
    if data.get('issue_date') is not None:
        qual.issue_date = datetime.strptime(data['issue_date'], '%Y-%m-%d').date() if data.get('issue_date') else None
    if data.get('valid_until') is not None:
        qual.valid_until = datetime.strptime(data['valid_until'], '%Y-%m-%d').date() if data.get('valid_until') else None
    if data.get('notes') is not None:
        qual.notes = data.get('notes')

    if qual.valid_until:
        days_until = (qual.valid_until - date.today()).days
        if days_until < 0:
            qual.status = '已过期'
        elif days_until <= 30:
            qual.status = '即将到期'
        else:
            qual.status = '有效'

    db.session.commit()

    return jsonify(qual.to_dict())

@qualifications_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_qualification(id):
    qual = Qualification.query.get(id)
    if not qual:
        return jsonify({'error': '资质不存在'}), 404

    db.session.delete(qual)
    db.session.commit()

    return jsonify({'message': '删除成功'})

@qualifications_bp.route('/names', methods=['GET'])
@jwt_required()
def get_qualification_names():
    return jsonify(Qualification.NAME_CHOICES)

@qualifications_bp.route('/expiring', methods=['GET'])
@jwt_required()
def get_expiring_qualifications():
    days = request.args.get('days', 90, type=int)
    from datetime import timedelta
    cutoff = date.today() + timedelta(days=days)
    quals = Qualification.query.filter(
        Qualification.valid_until <= cutoff,
        Qualification.valid_until >= date.today()
    ).order_by(Qualification.valid_until.asc()).all()

    return jsonify([q.to_dict() for q in quals])
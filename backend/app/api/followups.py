from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.followup import Followup
from app.models.partner import Partner
from app.models.project import Project

followups_bp = Blueprint('followups', __name__, url_prefix='/api/followups')

@followups_bp.route('', methods=['GET'])
@jwt_required()
def list_followups():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    partner_id = request.args.get('partner_id', type=int)
    project_id = request.args.get('project_id', type=int)
    method = request.args.get('method', '')

    query = Followup.query

    if partner_id:
        query = query.filter(Followup.partner_id == partner_id)
    if project_id:
        query = query.filter(Followup.project_id == project_id)
    if method:
        query = query.filter(Followup.method == method)

    query = query.order_by(Followup.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'items': [f.to_dict() for f in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

@followups_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_followup(id):
    followup = Followup.query.get(id)
    if not followup:
        return jsonify({'error': '跟进记录不存在'}), 404
    return jsonify(followup.to_dict())

@followups_bp.route('', methods=['POST'])
@jwt_required()
def create_followup():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data.get('content'):
        return jsonify({'error': '跟进内容不能为空'}), 400

    followup = Followup(
        partner_id=data.get('partner_id'),
        project_id=data.get('project_id'),
        method=data.get('method', '微信'),
        content=data.get('content'),
        next_followup_date=datetime.strptime(data['next_followup_date'], '%Y-%m-%d').date() if data.get('next_followup_date') else None,
        next_followup_content=data.get('next_followup_content'),
        created_by=user_id
    )

    db.session.add(followup)
    db.session.commit()

    return jsonify(followup.to_dict()), 201

@followups_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_followup(id):
    followup = Followup.query.get(id)
    if not followup:
        return jsonify({'error': '跟进记录不存在'}), 404

    data = request.get_json()

    if data.get('method') is not None:
        followup.method = data.get('method')
    if data.get('content') is not None:
        followup.content = data.get('content')
    if data.get('next_followup_date') is not None:
        followup.next_followup_date = datetime.strptime(data['next_followup_date'], '%Y-%m-%d').date() if data.get('next_followup_date') else None
    if data.get('next_followup_content') is not None:
        followup.next_followup_content = data.get('next_followup_content')

    db.session.commit()

    return jsonify(followup.to_dict())

@followups_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_followup(id):
    followup = Followup.query.get(id)
    if not followup:
        return jsonify({'error': '跟进记录不存在'}), 404

    db.session.delete(followup)
    db.session.commit()

    return jsonify({'message': '删��成功'})

@followups_bp.route('/methods', methods=['GET'])
@jwt_required()
def get_followup_methods():
    return jsonify(Followup.METHOD_CHOICES)
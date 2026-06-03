from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.project import Project
from app.models.partner import Partner
from app.models.user import User
from app.utils.validators import sanitize_input

projects_bp = Blueprint('projects', __name__, url_prefix='/api/projects')

@projects_bp.route('', methods=['GET'])
@jwt_required()
def list_projects():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    partner_id = request.args.get('partner_id', type=int)
    stage = request.args.get('stage', '')
    search = request.args.get('search', '')
    owner_id = request.args.get('owner_id', type=int)

    query = Project.query

    if partner_id:
        query = query.filter(Project.partner_id == partner_id)
    if stage:
        query = query.filter(Project.stage == stage)
    if owner_id:
        query = query.filter(Project.owner_id == owner_id)
    if search:
        query = query.filter(Project.name.contains(search))

    query = query.order_by(Project.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'items': [p.to_dict() for p in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

@projects_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_project(id):
    project = Project.query.get(id)
    if not project:
        return jsonify({'error': '项目不存在'}), 404
    return jsonify(project.to_dict())

@projects_bp.route('', methods=['POST'])
@jwt_required()
def create_project():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data.get('name'):
        return jsonify({'error': '项目名称不能为空'}), 400

    project = Project(
        name=sanitize_input(data.get('name')),
        partner_id=data.get('partner_id'),
        stage=data.get('stage', '线索'),
        budget=data.get('budget'),
        expected_close_date=datetime.strptime(data['expected_close_date'], '%Y-%m-%d').date() if data.get('expected_close_date') else None,
        owner_id=data.get('owner_id', user_id),
        collaborators=data.get('collaborators'),
        source=data.get('source'),
        industry=data.get('industry'),
        description=data.get('description'),
        created_by=user_id
    )

    db.session.add(project)
    db.session.commit()

    return jsonify(project.to_dict()), 201

@projects_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_project(id):
    project = Project.query.get(id)
    if not project:
        return jsonify({'error': '项目不存在'}), 404

    data = request.get_json()

    if data.get('name'):
        project.name = sanitize_input(data.get('name'))
    if data.get('partner_id') is not None:
        project.partner_id = data.get('partner_id')
    if data.get('stage') is not None:
        project.stage = data.get('stage')
    if data.get('budget') is not None:
        project.budget = data.get('budget')
    if data.get('expected_close_date') is not None:
        project.expected_close_date = datetime.strptime(data['expected_close_date'], '%Y-%m-%d').date() if data.get('expected_close_date') else None
    if data.get('owner_id') is not None:
        project.owner_id = data.get('owner_id')
    if data.get('collaborators') is not None:
        project.collaborators = data.get('collaborators')
    if data.get('source') is not None:
        project.source = data.get('source')
    if data.get('industry') is not None:
        project.industry = data.get('industry')
    if data.get('description') is not None:
        project.description = data.get('description')

    db.session.commit()

    return jsonify(project.to_dict())

@projects_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_project(id):
    project = Project.query.get(id)
    if not project:
        return jsonify({'error': '项目不存在'}), 404

    db.session.delete(project)
    db.session.commit()

    return jsonify({'message': '删除成功'})

@projects_bp.route('/stages', methods=['GET'])
@jwt_required()
def get_project_stages():
    return jsonify(Project.STAGE_CHOICES)
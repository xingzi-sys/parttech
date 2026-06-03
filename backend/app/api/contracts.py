import os
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models.contract import Contract, PaymentMilestone
from app.models.partner import Partner
from app.utils.validators import sanitize_input

contracts_bp = Blueprint('contracts', __name__, url_prefix='/api/contracts')

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@contracts_bp.route('', methods=['GET'])
@jwt_required()
def list_contracts():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    partner_id = request.args.get('partner_id', type=int)
    project_id = request.args.get('project_id', type=int)
    contract_type = request.args.get('contract_type', '')
    status = request.args.get('status', '')
    search = request.args.get('search', '')

    query = Contract.query

    if partner_id:
        query = query.filter(Contract.partner_id == partner_id)
    if project_id:
        query = query.filter(Contract.project_id == project_id)
    if contract_type:
        query = query.filter(Contract.contract_type == contract_type)
    if status:
        query = query.filter(Contract.status == status)
    if search:
        query = query.filter(Contract.contract_no.contains(search))

    query = query.order_by(Contract.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'items': [c.to_dict() for c in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

@contracts_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_contract(id):
    contract = Contract.query.get(id)
    if not contract:
        return jsonify({'error': '合同不存在'}), 404
    return jsonify(contract.to_dict())

@contracts_bp.route('', methods=['POST'])
@jwt_required()
def create_contract():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data.get('contract_no'):
        return jsonify({'error': '合同编号不能为空'}), 400

    if Contract.query.filter_by(contract_no=data.get('contract_no')).first():
        return jsonify({'error': '合同编号已存在'}), 400

    contract = Contract(
        contract_no=sanitize_input(data.get('contract_no')),
        project_id=data.get('project_id'),
        partner_id=data.get('partner_id'),
        contract_type=data.get('contract_type'),
        amount=data.get('amount'),
        parties=data.get('parties'),
        sign_date=datetime.strptime(data['sign_date'], '%Y-%m-%d').date() if data.get('sign_date') else None,
        start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date() if data.get('start_date') else None,
        end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data.get('end_date') else None,
        status=data.get('status', '起草'),
        notes=data.get('notes'),
        created_by=user_id
    )

    db.session.add(contract)
    db.session.commit()

    milestones = data.get('milestones', [])
    for m in milestones:
        milestone = PaymentMilestone(
            contract_id=contract.id,
            name=m.get('name'),
            amount=m.get('amount'),
            plan_date=datetime.strptime(m['plan_date'], '%Y-%m-%d').date() if m.get('plan_date') else None,
            status=m.get('status', '待付款')
        )
        db.session.add(milestone)

    db.session.commit()

    return jsonify(contract.to_dict()), 201

@contracts_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_contract(id):
    contract = Contract.query.get(id)
    if not contract:
        return jsonify({'error': '合同不存在'}), 404

    data = request.get_json()

    if data.get('contract_no'):
        contract.contract_no = sanitize_input(data.get('contract_no'))
    if data.get('project_id') is not None:
        contract.project_id = data.get('project_id')
    if data.get('partner_id') is not None:
        contract.partner_id = data.get('partner_id')
    if data.get('contract_type') is not None:
        contract.contract_type = data.get('contract_type')
    if data.get('amount') is not None:
        contract.amount = data.get('amount')
    if data.get('parties') is not None:
        contract.parties = data.get('parties')
    if data.get('sign_date') is not None:
        contract.sign_date = datetime.strptime(data['sign_date'], '%Y-%m-%d').date() if data.get('sign_date') else None
    if data.get('start_date') is not None:
        contract.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date() if data.get('start_date') else None
    if data.get('end_date') is not None:
        contract.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data.get('end_date') else None
    if data.get('status') is not None:
        contract.status = data.get('status')
    if data.get('notes') is not None:
        contract.notes = data.get('notes')

    if data.get('milestones'):
        PaymentMilestone.query.filter_by(contract_id=id).delete()
        for m in data.get('milestones'):
            milestone = PaymentMilestone(
                contract_id=id,
                name=m.get('name'),
                amount=m.get('amount'),
                plan_date=datetime.strptime(m['plan_date'], '%Y-%m-%d').date() if m.get('plan_date') else None,
                status=m.get('status', '待付款')
            )
            db.session.add(milestone)

    db.session.commit()

    return jsonify(contract.to_dict())

@contracts_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_contract(id):
    contract = Contract.query.get(id)
    if not contract:
        return jsonify({'error': '合同不存在'}), 404

    db.session.delete(contract)
    db.session.commit()

    return jsonify({'message': '删除成功'})

@contracts_bp.route('/<int:id>/upload', methods=['POST'])
@jwt_required()
def upload_attachment(id):
    contract = Contract.query.get(id)
    if not contract:
        return jsonify({'error': '合同不存在'}), 404

    if 'file' not in request.files:
        return jsonify({'error': '请选择文件'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '未选择文件'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(f"{contract.contract_no}_{file.filename}")
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        contract.attachment = filename
        db.session.commit()

        return jsonify({'message': '上传成功', 'filename': filename})

    return jsonify({'error': '不支持的文件类型'}), 400

@contracts_bp.route('/files/', methods=['GET'])
@jwt_required()
def download_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@contracts_bp.route('/types', methods=['GET'])
@jwt_required()
def get_contract_types():
    return jsonify(Contract.TYPE_CHOICES)

@contracts_bp.route('/statuses', methods=['GET'])
@jwt_required()
def get_contract_statuses():
    return jsonify(Contract.STATUS_CHOICES)
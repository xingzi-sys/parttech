from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.product import Product
from app.models.partner import Partner
from app.utils.validators import sanitize_input

products_bp = Blueprint('products', __name__, url_prefix='/api/products')

@products_bp.route('', methods=['GET'])
@jwt_required()
def list_products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    partner_id = request.args.get('partner_id', type=int)
    category = request.args.get('category', '')
    status = request.args.get('status', '')
    search = request.args.get('search', '')

    query = Product.query

    if partner_id:
        query = query.filter(Product.partner_id == partner_id)
    if category:
        query = query.filter(Product.category == category)
    if status:
        query = query.filter(Product.status == status)
    if search:
        query = query.filter(Product.name.contains(search))

    query = query.order_by(Product.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'items': [p.to_dict() for p in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

@products_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({'error': '产品不存在'}), 404
    return jsonify(product.to_dict())

@products_bp.route('', methods=['POST'])
@jwt_required()
def create_product():
    data = request.get_json()

    if not data.get('partner_id'):
        return jsonify({'error': '必须关联合作商'}), 400
    if not data.get('name'):
        return jsonify({'error': '产品名称不能为空'}), 400

    partner = Partner.query.get(data.get('partner_id'))
    if not partner:
        return jsonify({'error': '合作商不存在'}), 404

    product = Product(
        partner_id=data.get('partner_id'),
        name=sanitize_input(data.get('name')),
        category=data.get('category'),
        description=data.get('description'),
        scenarios=data.get('scenarios'),
        status=data.get('status', '在售')
    )

    db.session.add(product)
    db.session.commit()

    return jsonify(product.to_dict()), 201

@products_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({'error': '产品不存在'}), 404

    data = request.get_json()

    if data.get('name'):
        product.name = sanitize_input(data.get('name'))
    if data.get('category') is not None:
        product.category = data.get('category')
    if data.get('description') is not None:
        product.description = data.get('description')
    if data.get('scenarios') is not None:
        product.scenarios = data.get('scenarios')
    if data.get('status') is not None:
        product.status = data.get('status')

    db.session.commit()

    return jsonify(product.to_dict())

@products_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({'error': '产品不存在'}), 404

    db.session.delete(product)
    db.session.commit()

    return jsonify({'message': '删除成功'})

@products_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_product_categories():
    return jsonify(Product.CATEGORY_CHOICES)

@products_bp.route('/statuses', methods=['GET'])
@jwt_required()
def get_product_statuses():
    return jsonify(Product.STATUS_CHOICES)
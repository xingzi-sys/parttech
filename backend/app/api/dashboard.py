from datetime import datetime, date, timedelta
from sqlalchemy import func
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.partner import Partner
from app.models.project import Project
from app.models.contract import Contract, PaymentMilestone
from app.models.followup import Followup
from app.models.qualification import Qualification

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

@dashboard_bp.route('/overview', methods=['GET'])
@jwt_required()
def get_overview():
    total_partners = Partner.query.filter_by(status='活跃').count()
    total_projects = Project.query.count()
    total_contracts = Contract.query.count()

    total_contract_amount = db.session.query(func.sum(Contract.amount)).scalar() or 0

    active_projects = Project.query.filter(
        Project.stage.in_(['跟进', '方案', '商务', '签约'])
    ).count()

    return jsonify({
        'total_partners': total_partners,
        'total_projects': total_projects,
        'total_contracts': total_contracts,
        'total_contract_amount': float(total_contract_amount),
        'active_projects': active_projects
    })

@dashboard_bp.route('/partner-distribution', methods=['GET'])
@jwt_required()
def partner_distribution():
    by_type = db.session.query(
        Partner.type,
        func.count(Partner.id)
    ).filter(Partner.status == '活跃').group_by(Partner.type).all()

    by_level = db.session.query(
        Partner.level,
        func.count(Partner.id)
    ).filter(Partner.status == '活跃').group_by(Partner.level).all()

    by_status = db.session.query(
        Partner.status,
        func.count(Partner.id)
    ).group_by(Partner.status).all()

    return jsonify({
        'by_type': [{'name': t or '未分类', 'value': c} for t, c in by_type],
        'by_level': [{'name': l or '未分类', 'value': c} for l, c in by_level],
        'by_status': [{'name': s or '未分类', 'value': c} for s, c in by_status]
    })

@dashboard_bp.route('/project-funnel', methods=['GET'])
@jwt_required()
def project_funnel():
    stages = Project.STAGE_CHOICES
    counts = []
    for stage in stages:
        count = Project.query.filter_by(stage=stage).count()
        counts.append({'name': stage, 'value': count})

    return jsonify(counts)

@dashboard_bp.route('/contract-trend', methods=['GET'])
@jwt_required()
def contract_trend():
    month_count = request.args.get('month_count', 6, type=int)
    start_date = date.today() - timedelta(days=month_count * 30)

    contracts = Contract.query.filter(
        Contract.sign_date >= start_date
    ).all()

    monthly_data = {}
    for c in contracts:
        if c.sign_date:
            key = c.sign_date.strftime('%Y-%m')
            if key not in monthly_data:
                monthly_data[key] = {'count': 0, 'amount': 0}
            monthly_data[key]['count'] += 1
            monthly_data[key]['amount'] += float(c.amount or 0)

    result = []
    for i in range(month_count):
        d = date.today() - timedelta(days=(month_count - 1 - i) * 30)
        key = d.strftime('%Y-%m')
        result.append({
            'month': key,
            'count': monthly_data.get(key, {}).get('count', 0),
            'amount': monthly_data.get(key, {}).get('amount', 0)
        })

    return jsonify(result)

@dashboard_bp.route('/qualification-alerts', methods=['GET'])
@jwt_required()
def qualification_alerts():
    days = request.args.get('days', 90, type=int)
    cutoff = date.today() + timedelta(days=days)

    expiring = Qualification.query.filter(
        Qualification.valid_until <= cutoff,
        Qualification.valid_until >= date.today()
    ).order_by(Qualification.valid_until.asc()).limit(10).all()

    expired = Qualification.query.filter(
        Qualification.valid_until < date.today()
    ).order_by(Qualification.valid_until.desc()).limit(10).all()

    return jsonify({
        'expiring': [q.to_dict() for q in expiring],
        'expired': [q.to_dict() for q in expired],
        'expiring_count': len(expiring),
        'expired_count': len(expired)
    })

@dashboard_bp.route('/recent-activity', methods=['GET'])
@jwt_required()
def recent_activity():
    limit = request.args.get('limit', 10, type=int)

    recent_followups = Followup.query.order_by(Followup.created_at.desc()).limit(limit).all()

    activities = []
    for f in recent_followups:
        activities.append({
            'type': 'followup',
            'title': f'跟进记录',
            'description': f.content[:50] + '...' if f.content and len(f.content) > 50 else f.content,
            'partner_name': f.partner.name if f.partner else None,
            'creator_name': f.creator.real_name if f.creator else None,
            'created_at': f.created_at.isoformat() if f.created_at else None
        })

    recent_projects = Project.query.order_by(Project.created_at.desc()).limit(5).all()
    for p in recent_projects:
        activities.append({
            'type': 'project',
            'title': f'项目: {p.name}',
            'description': f'阶段: {p.stage}',
            'partner_name': p.partner.name if p.partner else None,
            'created_at': p.created_at.isoformat() if p.created_at else None
        })

    activities.sort(key=lambda x: x['created_at'] or '', reverse=True)
    return jsonify(activities[:limit])

@dashboard_bp.route('/payment-milestones', methods=['GET'])
@jwt_required()
def payment_milestones():
    upcoming = PaymentMilestone.query.filter(
        PaymentMilestone.status == '待付款',
        PaymentMilestone.plan_date >= date.today()
    ).order_by(PaymentMilestone.plan_date.asc()).limit(10).all()

    overdue = PaymentMilestone.query.filter(
        PaymentMilestone.status == '待付款',
        PaymentMilestone.plan_date < date.today()
    ).order_by(PaymentMilestone.plan_date.asc()).all()

    return jsonify({
        'upcoming': [{'id': m.id, 'name': m.name, 'amount': float(m.amount) if m.amount else 0, 'plan_date': m.plan_date.isoformat() if m.plan_date else None, 'contract_no': m.contract.contract_no if m.contract else None} for m in upcoming],
        'overdue': [{'id': m.id, 'name': m.name, 'amount': float(m.amount) if m.amount else 0, 'plan_date': m.plan_date.isoformat() if m.plan_date else None, 'contract_no': m.contract.contract_no if m.contract else None} for m in overdue]
    })
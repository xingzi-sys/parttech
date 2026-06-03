from datetime import datetime
from app.extensions import db

class PaymentMilestone(db.Model):
    __tablename__ = 'payment_milestones'
    id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contracts.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Numeric(15, 2))
    plan_date = db.Column(db.Date)
    actual_date = db.Column(db.Date)
    status = db.Column(db.String(20))
    notes = db.Column(db.Text)

    STATUS_CHOICES = ['待付款', '已付款', '逾期', '已取消']

    def to_dict(self):
        return {
            'id': self.id,
            'contract_id': self.contract_id,
            'name': self.name,
            'amount': float(self.amount) if self.amount else None,
            'plan_date': self.plan_date.isoformat() if self.plan_date else None,
            'actual_date': self.actual_date.isoformat() if self.actual_date else None,
            'status': self.status,
            'notes': self.notes
        }

class Contract(db.Model):
    __tablename__ = 'contracts'
    id = db.Column(db.Integer, primary_key=True)
    contract_no = db.Column(db.String(50), unique=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    partner_id = db.Column(db.Integer, db.ForeignKey('partners.id'))
    contract_type = db.Column(db.String(50))
    amount = db.Column(db.Numeric(15, 2))
    parties = db.Column(db.String(500))
    sign_date = db.Column(db.Date)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    attachment = db.Column(db.String(500))
    status = db.Column(db.String(20))
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    creator = db.relationship('User', backref='created_contracts')
    milestones = db.relationship('PaymentMilestone', backref='contract', lazy='dynamic', cascade='all, delete-orphan')

    TYPE_CHOICES = ['采购', '销售', '框架', '合作', '其他']
    STATUS_CHOICES = ['起草', '执��中', '已完成', '已终止']

    def to_dict(self):
        return {
            'id': self.id,
            'contract_no': self.contract_no,
            'project_id': self.project_id,
            'partner_id': self.partner_id,
            'partner_name': self.partner.name if self.partner else None,
            'contract_type': self.contract_type,
            'amount': float(self.amount) if self.amount else None,
            'parties': self.parties,
            'sign_date': self.sign_date.isoformat() if self.sign_date else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'attachment': self.attachment,
            'status': self.status,
            'notes': self.notes,
            'milestones': [m.to_dict() for m in self.milestones],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
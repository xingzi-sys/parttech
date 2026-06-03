from datetime import datetime
from app.extensions import db

class Partner(db.Model):
    __tablename__ = 'partners'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(50))
    credit_code = db.Column(db.String(18))
    registered_address = db.Column(db.String(500))
    website = db.Column(db.String(500))
    level = db.Column(db.String(20))
    status = db.Column(db.String(20))
    tags = db.Column(db.Text)
    description = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    contacts = db.relationship('Contact', backref='partner', lazy='dynamic', cascade='all, delete-orphan')
    products = db.relationship('Product', backref='partner', lazy='dynamic', cascade='all, delete-orphan')
    projects = db.relationship('Project', backref='partner', lazy='dynamic', cascade='all, delete-orphan')
    contracts = db.relationship('Contract', backref='partner', lazy='dynamic', cascade='all, delete-orphan')
    business_terms = db.relationship('BusinessTerm', backref='partner', lazy='dynamic', cascade='all, delete-orphan')
    qualifications = db.relationship('Qualification', backref='partner', lazy='dynamic', cascade='all, delete-orphan')

    TYPE_CHOICES = ['机房设备', '智算平台', '行业产品', '整体方案', '资金方', '其他']
    LEVEL_CHOICES = ['战略', '核心', '普通', '潜在']
    STATUS_CHOICES = ['活跃', '暂停', '终止']

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'credit_code': self.credit_code,
            'registered_address': self.registered_address,
            'website': self.website,
            'level': self.level,
            'status': self.status,
            'tags': self.tags.split(',') if self.tags else [],
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
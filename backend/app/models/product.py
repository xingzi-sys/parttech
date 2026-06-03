from datetime import datetime
from app.extensions import db

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    partner_id = db.Column(db.Integer, db.ForeignKey('partners.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50))
    description = db.Column(db.Text)
    scenarios = db.Column(db.Text)
    status = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    CATEGORY_CHOICES = ['算力资源', '平台软件', '行业应用', '配套服务', '资金支持']
    STATUS_CHOICES = ['在售', '即将发布', '停售']

    def to_dict(self):
        return {
            'id': self.id,
            'partner_id': self.partner_id,
            'partner_name': self.partner.name if self.partner else None,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'scenarios': self.scenarios,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
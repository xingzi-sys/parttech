from datetime import datetime
from app.extensions import db

class BusinessTerm(db.Model):
    __tablename__ = 'business_terms'
    id = db.Column(db.Integer, primary_key=True)
    partner_id = db.Column(db.Integer, db.ForeignKey('partners.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    term_type = db.Column(db.String(50))
    description = db.Column(db.Text)
    valid_from = db.Column(db.Date)
    valid_until = db.Column(db.Date)
    status = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = db.relationship('Product', backref='business_terms')

    TYPE_CHOICES = ['垫资', '返点', '账期', '价格体系', '技术支持', '其他']
    STATUS_CHOICES = ['生效中', '已过期', '待生效']

    def to_dict(self):
        return {
            'id': self.id,
            'partner_id': self.partner_id,
            'partner_name': self.partner.name if self.partner else None,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'term_type': self.term_type,
            'description': self.description,
            'valid_from': self.valid_from.isoformat() if self.valid_from else None,
            'valid_until': self.valid_until.isoformat() if self.valid_until else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
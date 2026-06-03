from datetime import datetime
from app.extensions import db

class Contact(db.Model):
    __tablename__ = 'contacts'
    id = db.Column(db.Integer, primary_key=True)
    partner_id = db.Column(db.Integer, db.ForeignKey('partners.id'), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    position = db.Column(db.String(100))
    role = db.Column(db.String(20))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    wechat = db.Column(db.String(100))
    is_primary = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    ROLE_CHOICES = ['决策者', '影响者', '执行者']

    def to_dict(self):
        return {
            'id': self.id,
            'partner_id': self.partner_id,
            'partner_name': self.partner.name if self.partner else None,
            'name': self.name,
            'position': self.position,
            'role': self.role,
            'phone': self.phone,
            'email': self.email,
            'wechat': self.wechat,
            'is_primary': self.is_primary,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
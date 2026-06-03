from datetime import datetime
from app.extensions import db

class Qualification(db.Model):
    __tablename__ = 'qualifications'
    id = db.Column(db.Integer, primary_key=True)
    partner_id = db.Column(db.Integer, db.ForeignKey('partners.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    cert_no = db.Column(db.String(100))
    issuer = db.Column(db.String(200))
    issue_date = db.Column(db.Date)
    valid_until = db.Column(db.Date)
    status = db.Column(db.String(20))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    NAME_CHOICES = ['机房等级', '信创', '等保', 'ISO9001', 'ISO27001', '高新技术企业', '其他']
    STATUS_CHOICES = ['有效', '即将到期', '已过期']

    def to_dict(self):
        return {
            'id': self.id,
            'partner_id': self.partner_id,
            'partner_name': self.partner.name if self.partner else None,
            'name': self.name,
            'cert_no': self.cert_no,
            'issuer': self.issuer,
            'issue_date': self.issue_date.isoformat() if self.issue_date else None,
            'valid_until': self.valid_until.isoformat() if self.valid_until else None,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
from datetime import datetime
from app.extensions import db

class Followup(db.Model):
    __tablename__ = 'followups'
    id = db.Column(db.Integer, primary_key=True)
    partner_id = db.Column(db.Integer, db.ForeignKey('partners.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    method = db.Column(db.String(20))
    content = db.Column(db.Text)
    next_followup_date = db.Column(db.Date)
    next_followup_content = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    creator = db.relationship('User', backref='followups')
    partner = db.relationship('Partner', backref='followups')

    METHOD_CHOICES = ['会议', '电话', '微信', '邮件', '现场']

    def to_dict(self):
        return {
            'id': self.id,
            'partner_id': self.partner_id,
            'partner_name': self.partner.name if self.partner else None,
            'project_id': self.project_id,
            'project_name': self.project.name if self.project else None,
            'method': self.method,
            'content': self.content,
            'next_followup_date': self.next_followup_date.isoformat() if self.next_followup_date else None,
            'next_followup_content': self.next_followup_content,
            'created_by': self.created_by,
            'creator_name': self.creator.real_name if self.creator else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
from datetime import datetime
from app.extensions import db

project_partners = db.Table('project_partners',
    db.Column('project_id', db.Integer, db.ForeignKey('projects.id'), primary_key=True),
    db.Column('partner_id', db.Integer, db.ForeignKey('partners.id'), primary_key=True)
)

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    partner_id = db.Column(db.Integer, db.ForeignKey('partners.id'))
    partners = db.relationship('Partner', secondary=project_partners, backref='projects_related')
    stage = db.Column(db.String(20))
    budget = db.Column(db.Numeric(15, 2))
    expected_close_date = db.Column(db.Date)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    collaborators = db.Column(db.Text)
    source = db.Column(db.String(100))
    industry = db.Column(db.String(100))
    description = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = db.relationship('User', foreign_keys=[owner_id], backref='owned_projects')
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_projects')
    contracts = db.relationship('Contract', backref='project', lazy='dynamic')
    followups = db.relationship('Followup', backref='project', lazy='dynamic')

    STAGE_CHOICES = ['线索', '跟进', '方案', '商务', '签约', '交付', '结项']

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'partner_id': self.partner_id,
            'partner_name': self.partner.name if self.partner else None,
            'stage': self.stage,
            'budget': float(self.budget) if self.budget else None,
            'expected_close_date': self.expected_close_date.isoformat() if self.expected_close_date else None,
            'owner_id': self.owner_id,
            'owner_name': self.owner.real_name if self.owner else None,
            'collaborators': self.collaborators.split(',') if self.collaborators else [],
            'source': self.source,
            'industry': self.industry,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
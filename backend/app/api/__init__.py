from flask import Flask
from app.api.auth import auth_bp

def register_blueprints(app: Flask):
    app.register_blueprint(auth_bp)

    from app.api.partners import partners_bp
    app.register_blueprint(partners_bp)

    from app.api.contacts import contacts_bp
    app.register_blueprint(contacts_bp)

    from app.api.products import products_bp
    app.register_blueprint(products_bp)

    from app.api.projects import projects_bp
    app.register_blueprint(projects_bp)

    from app.api.contracts import contracts_bp
    app.register_blueprint(contracts_bp)

    from app.api.followups import followups_bp
    app.register_blueprint(followups_bp)

    from app.api.business_terms import business_terms_bp
    app.register_blueprint(business_terms_bp)

    from app.api.qualifications import qualifications_bp
    app.register_blueprint(qualifications_bp)

    from app.api.users import users_bp
    app.register_blueprint(users_bp)

    from app.api.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)
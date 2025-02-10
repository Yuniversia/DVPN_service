from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Create databse or table if not exsist
def crt_db():
    from app import get_app
    import app.models.users
    import app.models.links
    import app.models.groups

    app = get_app()

    with app.app_context():
        if 'user' in db.metadata.tables:
            db.create_all()
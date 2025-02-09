import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager

from .extenssion import db

login_manager = LoginManager()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    email = db.Column(db.String)
    psw = db.Column(db.String(500), nullable=True)
    date = db.Column(db.DateTime, default=datetime.datetime.now())

    def __repr__(self):
        return f"<users {self.id}>"
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create databse or table if not exsist
def crt_db():
    from app import get_app
    import app.links

    app = get_app()

    with app.app_context():
        if 'user' in db.metadata.tables:
            db.create_all()

# Function, where we create new user
def crt_usr(name: str, email: str, psw: str):
    try:
        hash = generate_password_hash(psw) # Generete hash

        u = User(name=name, email=email, psw=hash)
        db.session.add(u)

        # Try to commit, and return True if sucsess
        try:
            db.session.commit()
            return True, 'Record added success'
        
        except Exception as e:
            db.session.reset()
            return False, e
        
    except Exception as e:
        return False, e
    
def get_usr(name: str):
    usr = db.session.query(User).filter_by(name=name).one_or_none()
    return usr

# Get password comparasion with usr psw
def get_psw(name: str, psw: str):
    db_psw = get_usr(name).psw

    # Return True if the password matches
    return check_password_hash(db_psw, psw)

def del_usr(name: str):
    res = db.session.query(User).filter_by(name=name).delete()

    if res > 0:
        return True
    return False
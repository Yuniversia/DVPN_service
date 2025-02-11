import datetime

from .ext import db

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager
from sqlalchemy.orm import relationship

login_manager = LoginManager()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    email = db.Column(db.String)
    psw = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)

    # group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=True)
    # group = relationship("Group", backref="users")

    # peer_id = db.Column(db.String(34), default=gen_peer_id)
    # ip = db.Column(db.String, nullable=True)
    # key = db.Column(db.String, nullable=True)

    def __repr__(self):
        return f"<users {self.id}>"
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


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
    try:
        db_psw = get_usr(name).psw

        # Return True if the password matches
        return check_password_hash(db_psw, psw)
    except:
        False

def del_usr(name: str):
    res = db.session.query(User).filter_by(name=name).delete()

    if res > 0:
        return True
    return False
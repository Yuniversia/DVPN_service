from .users import db, login_manager
from dotenv import load_dotenv
import os
from flask import Flask

load_dotenv()

def get_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config['SECRET_KEY'] = os.getenv('LOGIN_TIME')

    db.init_app(app)
    login_manager.init_app(app)

    from app.auth import auth

    app.register_blueprint(auth)
    
    return app
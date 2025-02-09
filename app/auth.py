from datetime import timedelta
from dotenv import load_dotenv
import os

from app.users import crt_usr, get_usr, get_psw, login_manager
from .forms import Sign_inForm, Sign_upForm
from .groups import get_groups, create_group, add_member

from flask_login import login_required, logout_user, login_user, current_user
from flask import Blueprint, request, jsonify, render_template, url_for, redirect, flash

load_dotenv()

login_manager.login_view = 'auth.index'

auth = Blueprint('auth', __name__)

@auth.route("/")
def index():

    sign_in = Sign_inForm()
    sign_up = Sign_upForm()

    return render_template('sign_in.html', sign_in=sign_in, sign_up=sign_up)

@auth.route("/sign_up", methods=['POST'])
def sign_up():
    try:
        data = request.form
        name = data['nickname']
        email = data['email']
        psw = data['password']

        res = crt_usr(name, email, psw)

        if not res[0]:
            flash("Nickname is not unique"), 500
            return redirect(url_for('auth.index')), 302

        login_user(get_usr(name), duration=timedelta(hours=int(os.getenv('LOGIN_TIME'))))
        return redirect(url_for('auth.person')), 302

    except Exception as e:
        return jsonify({'err': e}), 500
    
@auth.route("/sign_in", methods=['POST'])
def sign_in():
    try:
        form = Sign_inForm()
        name = form.nickname.data
        psw = form.password.data
        checkbox = form.checkbox.data

        res = get_psw(name, psw)

        if not res:
            flash("Nickname or password is incorrect")
            return redirect(url_for('auth.index'))
        
        if checkbox:
            login_user(get_usr(name), duration=timedelta(hours=int(os.getenv('LOGIN_TIME'))))
            return redirect(url_for('auth.person')), 302
        
        login_user(get_usr(name))
        return redirect(url_for('auth.person')), 302

    except Exception as e:
        return jsonify({'err': e}), 500
    
@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.index')), 302

@auth.route('/create_group')
@login_required
def grp():
    name = "Test_group"
    ip = "192.168.0.1/24"
    create_group(name, ip)
    return "success"

@auth.route('/add/<group_id>')
@login_required
def mem(group_id):
    name = "Test_group"
    ip = '192.168.0.2'
    group = add_member(current_user.id, group_id, ip)
    return "success"

@auth.route('/person')
@login_required
def person():
    # groups = get_groups(current_user.id)
    # print(groups)
    return render_template('prof.html', username=current_user.name)
    
@auth.route("/favicon.ico")
def icon():
    return '', 404
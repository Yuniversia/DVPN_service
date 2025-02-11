from datetime import timedelta
from dotenv import load_dotenv
import os


from .forms import Sign_inForm, Sign_upForm, GroupForm
from app.models import crt_usr, get_usr, get_psw, login_manager
from app.models import get_groups, create_group, add_member, get_group_members, delete_group_db, get_group
from app.validation import check_ip

from flask_login import login_required, logout_user, login_user, current_user
from flask import Blueprint, request, jsonify, render_template, url_for, redirect, flash

load_dotenv()

login_manager.login_view = 'auth.index'

auth = Blueprint('auth', __name__, template_folder="../templates", static_folder="../static")

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

@auth.route('/group', methods=["POST"])
@login_required
def group():

    form = GroupForm()
    name = form.network_name.data
    ip = form.ip.data
    key = form.encrypt_key.data

    user_id = current_user.id

    if check_ip(ip): #Check is ip corect 
        res = create_group(name, user_id, ip, key)
        if res[0]:
            return redirect(url_for("auth.person"))
        
        flash("Это имя группы не уникально", "name")
        return redirect(url_for("auth.person"))
    
    flash("Не правильный формат IP", "ip")
    return redirect(url_for("auth.person"))

@auth.route('/del/group', methods=["POST"])
@login_required
def delete_group():
    data = request.form
    group_id = data['group_id']

    res = delete_group_db(current_user.id, group_id)
    print(res)
    return redirect(url_for("auth.person"))

@auth.route('/group/<group_id>')
@login_required
def invite(group_id):

    if get_group(group_id):

        user_id = current_user.id

        res = add_member(user_id, group_id, admin=False)
        if res:
            return redirect(url_for("auth.person"))

        flash("Вы уже состоите в этой группе или произошла ошибка", "main")
        return redirect(url_for("auth.person"))
    
    flash("Пошёл нахуй, такой группы нет", "main")
    return redirect(url_for("auth.person"))

@auth.route('/person')
@login_required
def person():
    group = get_groups(current_user.id)
    group_form = GroupForm()
    return render_template('prof.html', user=current_user, 
                           group_form=group_form, groups=group, group_member=get_group_members)
    
@auth.route("/favicon.ico")
def icon():
    return '', 404

from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, PasswordField
from wtforms.validators import DataRequired

class Sign_inForm(FlaskForm):
    nickname = StringField("Nickname", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    checkbox = BooleanField("Remember me", default=False)
    submit = SubmitField("Sign In")

class Sign_upForm(FlaskForm):
    nickname = StringField("Nickname", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign In")

class GroupForm(FlaskForm):
    network_name = StringField("Network name", validators=[DataRequired()])
    ip = StringField("IP", validators=[DataRequired()], render_kw={"placeholder": "192.168.0.1/24"})
    encrypt_key = BooleanField("Encrypting", default=False)
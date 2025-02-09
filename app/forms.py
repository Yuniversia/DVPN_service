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
    net_name = StringField("Network name", validators=[DataRequired()])
    ip = StringField("IP", validators=[DataRequired()])
    mask = StringField("Mask", validators=[DataRequired()])
    submit = SubmitField("Sign In")
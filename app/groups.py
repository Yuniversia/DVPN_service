import uuid
import datetime

from .extenssion import db

from sqlalchemy.orm import relationship

def gen_peer_id():
    return uuid.uuid4().hex

class Group(db.Model):
    __tablename__ = "groups"

    id = db.Column(db.Integer, primary_key=True)
    network_name = db.Column(db.String, unique=True)
    ip = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())

class Group_member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    usr_uuid = db.Column(db.String(34), default=gen_peer_id)
    ip = db.Column(db.String)
    key = db.Column(db.String, nullable=True)

    group = relationship("Group", backref="group_member")
    user = relationship("User", backref="group_member")
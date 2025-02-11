import uuid
import datetime

from .ext import db
from app.validation import gen_ip

from sqlalchemy.orm import relationship

def gen_peer_id():
    return uuid.uuid4().hex

class Group(db.Model):
    __tablename__ = "groups"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    network_name = db.Column(db.String, unique=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    ip = db.Column(db.String)
    encryting = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)

    user = relationship("User", backref="groups")

class Group_member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    usr_uuid = db.Column(db.String(34), default=gen_peer_id)
    ip = db.Column(db.String)
    key = db.Column(db.String, nullable=True)
    admin = db.Column(db.Boolean, default=False)

    group = relationship("Group", backref="group_member")
    user = relationship("User", backref="group_member")

def get_groups(user_id: int):
    groups = db.session.query(Group_member).filter_by(user_id=user_id).fetchall_or_none()

    return groups

def get_group(group_id: int):
    group = db.session.query(Group).filter_by(id=group_id).one_or_none()

    return group

def get_member(user_id: int, group_id: int):
    res = db.session.query(Group_member).filter(Group_member.user_id == user_id, Group_member.group_id == group_id).one_or_none()

    print(res)

    if res:
        return True
    return False

def search_ip(group_id: int, ip: str) -> bool: 
    res = db.session.query(Group_member).filter(Group_member.ip == ip, Group_member.group_id == group_id).one_or_none()

    if res is None:
        return False
    return True

def create_group(name: str, author: int, ip: str, key: bool):
    g = Group(network_name=name, author_id=author, ip=ip, encryting=key)
    db.session.add(g)

    # Try to commit, and return True if sucsess
    try:
        db.session.commit()
        add_member(author, g.id, admin=True)
        return True, 'Record added success', g.id
    
    except Exception as e:
        db.session.reset()
        return False, e
    
def add_member(user_id: int, group_id: int, admin=False):
    group = get_group(group_id)

    member = get_member(user_id, group_id)

    if member is True:
        return False

    ip = gen_ip(group.ip, group_id)

    m = Group_member(user_id=user_id, group_id=group_id ,ip=ip, admin=admin)
    db.session.add(m)

    # Try to commit, and return True if sucsess
    try:
        db.session.commit()
        return True
    
    except Exception as e:
        db.session.reset()
        return False
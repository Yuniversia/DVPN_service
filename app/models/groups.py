import uuid
import datetime

from .ext import db
from app.validation import gen_ip
from .users import get_usr

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
    group_member = relationship("Group_member", foreign_keys="Group_member.group_id",
                                 back_populates="group", cascade="all, delete-orphan")
    token = relationship("Token", back_populates="group", cascade="all, delete-orphan")

class Group_member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    usr_uuid = db.Column(db.String(34), default=gen_peer_id)
    ip = db.Column(db.String)
    key = db.Column(db.String, nullable=True)
    admin = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=True)

    group = relationship("Group", back_populates="group_member", foreign_keys=[group_id])
    user = relationship("User", backref="group_member")


def get_member(user_id: int, group_id: int):
    res = db.session.query(Group_member).filter(Group_member.user_id == user_id, Group_member.group_id == group_id).one_or_none()

    return res

def get_group_members(group_id: int):
    res = db.session.query(Group_member).filter_by(group_id=group_id).all()

    return res

def add_member(user_id: int, group_id: int, admin=None):
    group = get_group(group_id)

    member = get_member(user_id, group_id)

    if member:
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

def leave_member(user_id: int, group_id: int):
    member = get_member(user_id, group_id)

    try:
        db.session.delete(member)
        db.session.commit()
        return True
    except:
        return False


def delete_group_member(author_id: int, group_id: int, user_id: int):
    group = get_member(author_id, group_id)

    if group is None:
        return False

    if group.admin == group_id:
        return False
    
    leave_member(user_id, group_id)
    return True
    

def create_group(name: str, author: int, ip: str, key: bool):
    g = Group(network_name=name, author_id=author, ip=ip, encryting=key)
    db.session.add(g)

    # Try to commit, and return True if sucsess
    try:
        db.session.commit()
        add_member(author, g.id, admin=g.id)
        return True, 'Record added success', g.id
    
    except Exception as e:
        db.session.reset()
        return False, e
    
def get_groups(user_id: int):
    groups = db.session.query(Group_member).filter_by(user_id=user_id).all()

    return groups

def get_group(group_id: int):
    group = db.session.query(Group).filter_by(id=group_id).one_or_none()

    return group
    
def delete_group_db(user_id: int, group_id: int):
    group = get_group(group_id)

    if user_id == group.author_id:
        db.session.delete(group)
        db.session.commit()
        return True
    return False

    

def search_ip(group_id: int, ip: str) -> bool: 
    res = db.session.query(Group_member).filter(Group_member.ip == ip, Group_member.group_id == group_id).one_or_none()

    if res is None:
        return False
    return True
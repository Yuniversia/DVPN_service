
import uuid
from datetime import datetime, timedelta

from .groups import get_group_members
from .ext import db

from sqlalchemy.orm import relationship

def gen_link_token():
    return uuid.uuid4().hex

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    token = db.Column(db.String(34), unique=True, default=gen_link_token)

    created_at = db.Column(db.DateTime, default=datetime.now)
    expires_at = db.Column(db.DateTime, nullable=False)
    max_uses = db.Column(db.Integer, nullable=False)
    used_count = db.Column(db.Integer, default=0)

    group = relationship("Group", backref="link", foreign_keys=[group_id])
    user = relationship("User", backref="link")

    def __repr__(self):
        return f"<links {self.id}>"
    
    def is_expired(self):
        return datetime.now() > self.expires_at

    def has_uses_left(self):
        return self.used_count < self.max_uses
    
def cleanup_links():
    # Удаляем просроченные ссылки перед каждым запросом
    expired_links = Link.query.filter(Link.expires_at <= datetime.now()).all()
    for link in expired_links:
        db.session.delete(link)
    db.session.commit()

def add_used_count(link):
    link.used_count += 1
    if not link.has_uses_left():
        db.session.delete(link)
    db.session.commit()

def get_token_link(token: str):
    link = Link.query.filter_by(token=token).one_or_none()
    return link

def delete_token_link(link):
    db.session.delete(link)
    db.session.commit()

def create_group_link(author_id: int, group_id: int, minutes: int, max_uses: int):
    new_link = Link(author_id=author_id, group_id=group_id, 
            expires_at=datetime.now() + timedelta(minutes=minutes),
            max_uses=max_uses)
    
    db.session.add(new_link)
    db.session.commit()

    return new_link.token
    
class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(34), unique=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))

    group = relationship("Group", back_populates="token")
    user = relationship("User", backref="token")

def get_author_token(author_id: int, group_id: int):
    res = db.session.query(Token).filter(Token.author_id == author_id,
                                                 Token.group_id == group_id).one_or_none()
    
    return res


def create_token(author_id: int, group_id: int):
    
    user_token = get_author_token(author_id, group_id)

    if user_token is not None:
        return user_token.token

    token = uuid.uuid4().hex

    t = Token(token=token, author_id=author_id, group_id=group_id)
    db.session.add(t)

    try:
        db.session.commit()
        return token
    except:
        return None
    
def get_token(token: str):
     res = db.session.query(Token).filter_by(token=token).one_or_none()

     return res
    
def get_group_peer(token: str):
    token_rec = get_token(token)

    members = get_group_members(token_rec.group_id)
    peer_list = []

    for member in members:
        member_json = dict(name=member.user.name, id=member.usr_uuid,
                            addr=member.ip)
        
        if member.key is not None:
            member_json.update({"crypto": {"key": f"{member.key}"}})

        peer_list.append(member_json)

    return peer_list

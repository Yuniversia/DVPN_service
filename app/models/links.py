from .ext import db
import uuid
from .groups import get_group_members

from sqlalchemy.orm import relationship

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    uses = db.Column(db.Integer)
    end_date = db.Column(db.Float)

    user = relationship("User", backref="link")

    def __repr__(self):
        return f"<links {self.id}>"
    
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
                            addr=member.ip, key=member.key)
        peer_list.append(member_json)

    return peer_list

from .ext import db
import uuid

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
    token = db.Column(db.String(34))
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
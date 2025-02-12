from .ext import db

from sqlalchemy.orm import relationship

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    uses = db.Column(db.Integer)
    end_date = db.Column(db.Float)

    user = relationship("User", backref="link")

    def __repr__(self):
        return f"<links {self.id}>"

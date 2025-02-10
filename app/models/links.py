from .ext import db

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String)
    uses = db.Column(db.Integer)
    end_date = db.Column(db.Float)

    def __repr__(self):
        return f"<links {self.id}>"

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint

db = SQLAlchemy()

# This is the User class that holds an Id, username, password and the time the account was created.
# It returns the Id, username, and password


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    # Unique username unique=True,
    username = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # __repr__ returns a String representation of the Users class when
    # we print out an object of type Users
    def __repr__(self) -> str:
        return f"ID: {self.id}, Username: {self.username}, Password: {self.password}"


# This is the Guide class
likes = db.Table('likes',
                 db.Column('user_id', db.Integer, db.ForeignKey(
                     'user.id'), primary_key=True),
                 db.Column('guide_id', db.Integer, db.ForeignKey(
                     'guide.id'), primary_key=True)
                 )


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    guide_id = db.Column(db.Integer, db.ForeignKey('guide.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    report_type = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def serialize(self):
        return {
            "id": self.id,
            "guide_id": self.guide_id,
            "report_type": self.report_type,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Guide(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reports = db.relationship('Report', backref='guide', lazy=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    num_likes = db.Column(db.Integer, default=0)
    user = db.relationship('User', backref='guides')
    liked_by = db.relationship(
        'User', secondary=likes, backref=db.backref('liked_guides', lazy='dynamic'))
    comments = db.relationship(
        'Comment', backref='guide', cascade="all, delete-orphan", lazy=True)
    title = db.Column(db.String(255), nullable=False)

    def __repr__(self) -> str:
        string = f"ID: {self.id}, Num_likes: {self.num_likes}, Title: {self.title}, Content: {self.content}, Created_At: {self.created_at}, Comments: {self.comments}, User: {self.user}"
        return string

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "num_likes": self.num_likes,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

# This is the Comment class


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    guide_id = db.Column(db.Integer, db.ForeignKey('guide.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    user = db.relationship('User', backref='comments')
    replies = db.relationship('Reply', backref='comment', lazy=True)

    def __repr__(self) -> str:
        return f"<Comment: {self.id} | Guide {self.guide_id} | {self.user}>"

    def serialize(self):
        return {
            "id": self.id,
            "guide_id": self.guide_id,
            "content": self.content,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

# This is the Reply class


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    # 'like', 'comment', 'reply'
    type = db.Column(db.String(50), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    link = db.Column(db.String(255), nullable=False)
    user = db.relationship('User', backref='notifications')


class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey(
        'comment.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    user = db.relationship('User', backref='reply')

    def __repr__(self) -> str:
        return f"<Reply: {self.id} | Comment {self.comment_id} | {self.user}>"

    def serialize(self):
        return {
            "id": self.id,
            "comment_id": self.comment_id,
            "content": self.content,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

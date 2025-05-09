from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint
from datetime import datetime

db = SQLAlchemy()

# Association table for Likes (User <-> Guide) - correctly placed
likes = db.Table('likes',
                 db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
                 db.Column('guide_id', db.Integer, db.ForeignKey('guide.id', ondelete='CASCADE'), primary_key=True),
                 db.Column('created_at', db.DateTime, default=datetime.utcnow) # Optional: track when like happened
                 )

# This is the User class that holds an Id, username, password and the time the account was created.
# It returns the Id, username, and password


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # Increased length for hashed passwords
    description = db.Column(db.Text, nullable=True)
    profile_pic = db.Column(db.String(200), nullable=True, default='default.jpg')
    is_admin = db.Column(db.Boolean, nullable=False, default=False) # Reverted temporary default
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships with back_populates
    guides_authored = db.relationship('Guide', back_populates='author', lazy='dynamic', cascade='all, delete-orphan')
    comments_made = db.relationship('Comment', back_populates='commenter', lazy='dynamic', cascade='all, delete-orphan')
    replies_made = db.relationship('Reply', back_populates='replier', lazy='dynamic', cascade='all, delete-orphan')
    reports_made = db.relationship('Report', back_populates='reporter', lazy='dynamic', cascade='all, delete-orphan')
    notifications_received = db.relationship('Notification', back_populates='recipient', lazy='dynamic', cascade='all, delete-orphan')
    
    liked_guides = db.relationship('Guide',
                                 secondary=likes,
                                 back_populates='liked_by_users',
                                 lazy='dynamic')

    # __repr__ returns a String representation of the Users class when
    # we print out an object of type Users
    def __repr__(self) -> str:
        return f"<User ID: {self.id}, Username: {self.username}>"

    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'description': self.description,
            'profile_pic': self.profile_pic,
            'is_admin': self.is_admin  # Add to serialization if needed elsewhere
        }


# This is the Guide class


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    guide_id = db.Column(db.Integer, db.ForeignKey('guide.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    report_type = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships with back_populates
    reporter = db.relationship('User', back_populates='reports_made')
    reported_guide = db.relationship('Guide', back_populates='reports_on_guide')

    def __repr__(self):
        return f"<Report ID: {self.id}, Type: {self.report_type}, Guide ID: {self.guide_id}>"
    
    def serialize(self):
        return {
            "id": self.id,
            "guide_id": self.guide_id,
            "user_id": self.user_id, # or "reporter_username": self.reporter.username
            "report_type": self.report_type,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Guide(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Foreign key to User (author)
    # The 'author' property will be available on Guide instances due to the backref from User.guides
    # No need for: user = db.relationship('User', backref='guides') as it conflicts
    
    reports_on_guide = db.relationship('Report', back_populates='reported_guide', lazy='dynamic', cascade='all, delete-orphan')
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    num_likes = db.Column(db.Integer, default=0)
    
    # The relationship from User.liked_guides creates guide.liked_by_users.
    # So, the explicit 'liked_by' relationship below is redundant and causes conflict.
    # We will remove it.
    # liked_by = db.relationship(
    #     'User', secondary=likes, backref=db.backref('liked_guides', lazy='dynamic'))
        
    comments_on_guide = db.relationship('Comment', back_populates='guide', lazy='dynamic', cascade='all, delete-orphan')
    title = db.Column(db.String(255), nullable=False)

    # Relationships with back_populates
    author = db.relationship('User', back_populates='guides_authored')

    def __repr__(self) -> str:
        author_username = self.author.username if self.author else "N/A"
        return f"<Guide ID: {self.id}, Title: {self.title}, Author: {author_username}>"

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "num_likes": self.num_likes,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "author_username": self.author.username if self.author else "Unknown"
        }

# This is the Comment class


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    guide_id = db.Column(db.Integer, db.ForeignKey('guide.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # The 'commenter' property will be available on Comment instances due to the backref from User.comments.
    # No need for: user = db.relationship('User', backref='comments') as it conflicts.
    # user = db.relationship('User', backref='comments') # THIS LINE IS THE CULPRIT AND WILL BE REMOVED
    
    replies = db.relationship('Reply', back_populates='parent_comment', lazy='dynamic', cascade='all, delete-orphan')
    # Optional: if you want a direct link from comment to guide object (besides guide_id)
    guide = db.relationship('Guide', back_populates='comments_on_guide')

    # Relationships with back_populates
    commenter = db.relationship('User', back_populates='comments_made')

    def __repr__(self) -> str:
        commenter_username = self.commenter.username if self.commenter else "N/A"
        return f"<Comment ID: {self.id}, Guide ID: {self.guide_id}, By: {commenter_username}>"

    def serialize(self):
        return {
            "id": self.id,
            "guide_id": self.guide_id,
            "content": self.content,
            "user_id": self.user_id, # or "commenter_username": self.commenter.username
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

# This is the Reply class


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    link = db.Column(db.String(255), nullable=False)
    # Removed user relationship as it's covered by backref from User.notifications
    # user = db.relationship('User', backref='notifications') 

    # Relationship with back_populates
    recipient = db.relationship('User', back_populates='notifications_received')

    def __repr__(self):
        return f"<Notification ID: {self.id}, Type: {self.type}, User ID: {self.user_id}>"

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "content": self.content,
            "type": self.type,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "link": self.link
        }


class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships with back_populates
    replier = db.relationship('User', back_populates='replies_made')
    parent_comment = db.relationship('Comment', back_populates='replies')

    def __repr__(self) -> str:
        replier_username = self.replier.username if self.replier else "N/A"
        return f"<Reply ID: {self.id}, Comment ID: {self.comment_id}, By: {replier_username}>"

    def serialize(self):
        return {
            "id": self.id,
            "comment_id": self.comment_id,
            "content": self.content,
            "user_id": self.user_id, # or "replier_username": self.replier.username
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

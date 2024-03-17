from datetime import datetime

from marshmallow import fields, validate
from marshmallow.validate import Length, And, Regexp

from models.user import User
from models.media import Media
from init import db, ma


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created = db.Column(db.DateTime, default=db.func.current_timestamp())

    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    media_id = db.Column(db.Integer, db.ForeignKey('media.id'), nullable=False)

    parent = db.relationship(
        'Comment',
        remote_side=[id], 
        backref='children'
    )
    user = db.relationship(
        'User',
        backref='comments'
    )
    media = db.relationship(
        'Media',
        backref='comments'
    )


class CommentSchema(ma.Schema):

    id = fields.Int()
    user = fields.Nested(
        'UserSchema',
        only=['username']
    )
    media = fields.Nested(
        'MediaSchema',
        only=['title', 'category']
    )


    class Meta:
        fields = (
            'id',
            'media',
            'user',
            'content',
            'created',
            'parent_id'
        )


comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)
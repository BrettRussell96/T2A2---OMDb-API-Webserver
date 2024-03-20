# external import for schema fields
from marshmallow import fields
# local imports for model relatins, SQLAlchemy and marshmallow
from models.user import User
from models.media import Media
from init import db, ma

# create comment model
class Comment(db.Model):
    # set tablename to comments
    __tablename__ = "comments"
    # define columns and datatypes
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created = db.Column(db.DateTime, default=db.func.current_timestamp())
    # establish foreign keys
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    media_id = db.Column(db.Integer, db.ForeignKey('media.id'), nullable=False)
    # set relationships with other models
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

# create schema class
class CommentSchema(ma.Schema):
    # set field data types
    id = fields.Int()
    content = fields.Str()
    created = fields.DateTime(
        format="%Y-%m-%d T%H:%M"
    )
    # set fields to be shown from foreign keys
    user = fields.Nested(
        'UserSchema',
        only=['username']
    )
    media = fields.Nested(
        'MediaSchema',
        only=['title', 'category']
    )

    parent_id = fields.Int(allow_none=True)
    # specify nesting for child comments
    children = fields.Nested('self', many=True, exclude=('parent',))
    # create meta class to show which fields are displayed
    class Meta:
        fields = (
            'id',
            'media',
            'user',
            'content',
            'created',
            'parent_id'
        )

# create schema instances for importing
comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)
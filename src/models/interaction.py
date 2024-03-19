# built in import for category enum
import enum
# external imports for schemas, enum and check constraint
from marshmallow import fields, validate
from marshmallow_enum import EnumField
from sqlalchemy import CheckConstraint, Enum
# local imports for forein key schema, SQLAlchemy and marshmallow
from .media import MediaSchema
from init import db, ma

# class for enum categories 
class InteractionEnum(enum.Enum):
    yes = "yes"
    no = "no"


# class for interaction model
class Interaction(db.Model):
    # set table name to interaction
    __tablename__ = "interaction"
    # define columns and datatypes
    # set id to primary key
    id = db.Column(db.Integer, primary_key=True)
    # set watched to enum data type 
    watched = db.Column(Enum(InteractionEnum), default=InteractionEnum.no)
    rating = db.Column(db.Integer)
    # set watchlist to enum
    watchlist = db.Column(Enum(InteractionEnum), default=InteractionEnum.no)
    # define foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    media_id = db.Column(db.Integer, db.ForeignKey('media.id'), nullable=False)
    # set user and media relationship
    user = db.relationship(
        'User',
        back_populates='interactions'
    )
    media = db.relationship(
        'Media',
        back_populates='interactions'
    )
    # define check constraint for ratings to be between 0 - 10 
    __table_args__ = (
        (CheckConstraint(
            'rating >= 0 AND rating <= 10', name='check_rating_range'
        ),
    )
    )

# create schema class
class InteractionSchema(ma.Schema):
    # set field data type
    id = fields.Int()
    watched = EnumField(InteractionEnum, by_value=True)
    # set valid range for rating
    rating = fields.Integer(validate=validate.Range(min=0, max=10))
    watchlist = EnumField(InteractionEnum, by_value=True)
    user_id = fields.Int()
    media_id = fields.Int()
    # nested fields for foreign keys to show what fields will be shown
    user = fields.Nested(
        'UserSchema',
        only = ['username', 'location']
    )
    media = fields.Nested(
        MediaSchema,
        only = ('id', 'title', 'year', 'category')
    )
    # class to specify fields in serialised representation
    class Meta:
        fields = (
            'id',
            'media',
            'watched',
            'rating',
            'watchlist',
            'user'
        )
        ordered = True
    
# instances of schema for single or multiple records
interaction_schema = InteractionSchema()
interactions_schema = InteractionSchema(many=True)


import enum

from marshmallow import fields, validate
from marshmallow_enum import EnumField
from sqlalchemy import CheckConstraint, Enum

from .media import MediaSchema
from init import db, ma


class InteractionEnum(enum.Enum):
    yes = "yes"
    no = "no"



class Interaction(db.Model):
    __tablename__ = "interaction"

    id = db.Column(db.Integer, primary_key=True)
    watched = db.Column(Enum(InteractionEnum), default=InteractionEnum.no)
    rating = db.Column(db.Integer)
    watchlist = db.Column(Enum(InteractionEnum), default=InteractionEnum.no)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    media_id = db.Column(db.Integer, db.ForeignKey('media.id'), nullable=False)

    user = db.relationship(
        'User',
        back_populates='interactions'
    )
    media = db.relationship(
        'Media',
        back_populates='interactions'
    )

    __table_args__ = (
        (CheckConstraint(
            'rating >= 0 AND rating <= 10', name='check_rating_range'
        ),
    )
    )


class InteractionSchema(ma.Schema):
    
    id = fields.Int()
    watched = EnumField(InteractionEnum, by_value=True)
    rating = fields.Integer(validate=validate.Range(min=0, max=10))
    watchlist = EnumField(InteractionEnum, by_value=True)
    user_id = fields.Int()
    media_id = fields.Int()
    user = fields.Nested(
        'UserSchema',
        only = ['username', 'location']
    )
    media = fields.Nested(
        MediaSchema,
        only = ('id', 'title', 'year', 'category')
    )

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
    

interaction_schema = InteractionSchema()
interactions_schema = InteractionSchema(many=True)


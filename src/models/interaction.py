import enum

from marshmallow import fields, validate
from marshmallow_enum import EnumField
from sqlalchemy import CheckConstraint, Enum



from init import db, ma


class CategoryEnum(enum.Enum):
    yes = "yes"
    no = "no"



class Interaction(db.Model):
    __tablename__ = "interaction"

    id = db.Column(db.Integer, primary_key=True)
    watched = db.Column(Enum(CategoryEnum), default=CategoryEnum.no)
    rating = db.Column(db.Integer)
    watchlist = db.Column(Enum(CategoryEnum), default=CategoryEnum.no)

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
        CheckConstraint(
            'rating >= 0 AND rating <= 10', name='check_rating_range'
        )
    )


class InteractionSchema(ma.Schema):

    rating = fields.Integer(validate=validate.Range(min=0, max=10))

    user = fields.Nested(
        'UserSchema',
        only = ['username', 'location']
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


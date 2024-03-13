from init import db, ma

from marshmallow import fields
from marshmallow.validate import Length, And, Regexp


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    location = db.Column(db.String)
    is_admin = db.Column(db.Boolean, default=False)

    interactions = db.relationship(
        'Interaction',
        back_populates='user'
    )


class UserSchema(ma.Schema):

    username = fields.String(
        required=True,
        validate=And(
            Length(
                min=5,
                error="Username must be at least 5 characters."
            ),
            Regexp(
                '^[a-zA-Z0-9_-.]+$',
                error="Username must unspaced with valid characters."
            )
        )
    )

    class Meta:
        fields = (
            'id',
            'username',
            'email',
            'password',
            'location',
            'is_admin'
            )


user_schema = UserSchema(exclude=['password'])
users_schema = UserSchema(many=True, exclude=['password'])


class UserPublicSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'location')


users_public_schema = UserPublicSchema(many=True)

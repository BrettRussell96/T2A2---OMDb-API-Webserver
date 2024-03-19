# external imports for schemas
from marshmallow import fields
from marshmallow.validate import Length, And, Regexp
# local imports for marshmallow and SQLAlchemy
from init import db, ma

# create User model
class User(db.Model):
    # set tablename to users
    __tablename__ = "users"
    # use db to define columns and data types 
    # set id as primary key 
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    location = db.Column(db.String)
    is_admin = db.Column(db.Boolean, default=False)
    # establish relationship between User and Interaction
    interactions = db.relationship(
        'Interaction',
        back_populates='user'
    )

# create schema class
class UserSchema(ma.Schema):
    # define the data type, requirement and validaiton criteria for username 
    username = fields.String(
        required=True,
        validate=And(
            Length(
                min=5,
                error="Username must be at least 5 characters."
            ),
            Regexp(
                '^[a-zA-Z0-9_.-]+$',
                error="Username must be unspaced with valid characters."
            )
        )
    )
    # define datatype, requirement, and validation criteria for password 
    password = fields.String(
        required=True,
        validate=And(
            Length(
                min=5,
                error="Password must be at least 5 characters."
            ),
            Regexp(
                '^[a-zA-Z0-9_.-]+$',
                error="Password must be unspaced with valid characters."
            )
        )
    )
    # class to specify fields included in serialised representation
    class Meta:
        fields = (
            'id',
            'username',
            'email',
            'password',
            'location',
            'is_admin'
        )
        # specify correct order
        ordered = True

# create schema instances 
# for displaying user info
user_schema = UserSchema(exclude=['password'])
# for handling validation in user registration
user_registration_schema = UserSchema()
# for handling validation in user updates
user_schema_partial = UserSchema(partial=True)

# public schema for showing only non sensitive data
class UserPublicSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'location')

# used for displaying listed user info
users_public_schema = UserPublicSchema(many=True)

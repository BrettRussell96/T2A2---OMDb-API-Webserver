from datetime import timedelta
import functools

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from psycopg2 import errorcodes
from werkzeug.security import generate_password_hash

from init import db, bcrypt
from models.user import User, user_schema, users_public_schema

user_bp = Blueprint('user', __name__, url_prefix='/user')


def authorise_as_admin(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        stmt = db.select(User).filter_by(id=user_id)
        user = db.session.scalar(stmt)

        if user.is_admin:
            return fn(*args, **kwargs)
        else:
            return {
                "Error": "Not authorised to delete this user"
                }, 403
    
    return wrapper


@user_bp.route("/")
def get_all_users():
    users = User.query.all()
    result = users_public_schema.dump(users)
    return {"users": result}, 200


@user_bp.route("/location")
def get_users_by_location():
    location_query = request.args.get('location')
    if not location_query:
        return {
            "Error": "Location parameter is required"
            }, 400
    
    users = User.query.filter(
        User.location.ilike(f"%{location_query}%")
        ).all()
    return users_public_schema.dump(users), 200


@user_bp.route("/register", methods=["POST"])
def user_register():
    try:
        body_data = request.get_json()
        username = body_data.get('username')

        if ' ' in username:
            return {
                "Error": "Username cannot contain spaces"
            }, 400
        
        user = User(
            username=username,
            email=body_data.get('email'),
            location=body_data.get('location')
        )
        password = body_data.get('password')

        if password:
            user.password = bcrypt.generate_password_hash(password).decode(
                'utf-8'
                )

        db.session.add(user)
        db.session.commit()

        return user_schema.dump(user), 201

    except IntegrityError as err:
        db.session.rollback()
        error_code = err.orig.pgcode
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {
                "Error": f"The {err.orig.diag.column_name}"
                " is required to create a user."
                }, 400
        elif error_code == errorcodes.UNIQUE_VIOLATION:
            column_name = err.orig.diag.constraint_name
            if 'username' in column_name:
                return {
                    "Error": "That username is already taken."
                    " Please choose another one."
                    }, 400
            elif 'email' in column_name:
                return {
                    "Error": "That email is already registered."
                    " Please use a different email."
                    }, 400


@user_bp.route("/login", methods=["POST"])
def user_login():
    body_data = request.get_json()
    login_field = body_data.get("username/email")
    stmt = db.select(User).filter(
        or_(User.email == login_field, User.username == login_field)
        )
    user = db.session.scalar(stmt)

    if user and bcrypt.check_password_hash(
            user.password,
            body_data.get('password')
            ):
        token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(days=7)
            )
        return {
            "username": user.username,
            "email": user.email, "token": token,
            "is_admin": user.is_admin
            }
    else:
        return {
            "Error": "Username or password is invalid"
            }, 401


@user_bp.route("/<string:username>", methods=["PUT", "PATCH"])
@jwt_required()
def edit_user(username):
    current_user_id = get_jwt_identity()
    user = User.query.filter_by(id=current_user_id, username=username).first()

    if not user:
        return jsonify(
            {
                "Error": f"User {username} could not be found"
                }
            ), 404
    
    data = request.get_json()
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    user.location = data.get('location', user.location)

    if data.get('password'):
        user.password = generate_password_hash(data['password'])

    db.session.commit()

    return jsonify(
        {
            "Messsage": "User updated successfully"
            }
        ), 200


@user_bp.route("/<int:user_id>", methods=["DELETE"])
@jwt_required()
@authorise_as_admin
def delete_user(user_id):
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)

    if user:
        db.session.delete(user)
        db.session.commit()

        return jsonify(
            {
                "Message": f"User {user.username} deleted successfully"
                }
            ), 200
    else:
        return jsonify(
            {
                "Error": f"User with id {user_id} not found"
                }
            ), 404

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
from models.user import user_schema_partial, user_registration_schema

user_bp = Blueprint('user', __name__, url_prefix='/user')


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
    body_data = request.get_json()
    try:
        errors = user_registration_schema.validate(body_data)
        if errors:
            return jsonify(errors), 400
        
        username = body_data.get('username')
        email = body_data.get('email')
        password = body_data.get('password')

        
        user = User(
            username=username,
            email=email,
            location=body_data.get('location')
        )

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
                "Error": f"The {err.orig.diag.column_name} field"
                " is required to create a user."
                }, 400
        if error_code == errorcodes.UNIQUE_VIOLATION:
            column_name = err.orig.diag.constraint_name
            if 'username' in column_name:
                return {
                    "Error": "That username is already taken."
                    " Please choose another one."
                    }, 400
            if 'email' in column_name:
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


@user_bp.route("/", methods=["PUT", "PATCH"])
@jwt_required()
def edit_user():
    current_user_id = get_jwt_identity()
    current_user = User.query.filter_by(id=current_user_id).first()
    if not current_user:
        return jsonify({
            "Error": f"User could not be found."
        }), 404
    
    data = request.get_json()

    try: 
        errors = user_schema_partial.validate(data)
        if errors:
            return jsonify(errors), 400  

        if 'username' in data:
            current_user.username = data['username']
        if 'email' in data:
            current_user.email = data['email']
        if 'location' in data:
            current_user.location = data['location']
        if 'password' in data:
            current_user.password = generate_password_hash(data['password'])
        
        db.session.commit()

        return jsonify(
            {
                "Messsage": "User updated successfully"
                }
            ), 200
    except IntegrityError as err:
        db.session.rollback()
        error_code = err.orig.pgcode
        if error_code == errorcodes.UNIQUE_VIOLATION:
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


@user_bp.route("/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    current_user_id = get_jwt_identity()
    stmt = db.select(User).filter_by(id=current_user_id)
    current_user = db.session.scalar(stmt)

    if not current_user:
        return {
            "Error": "User not found."
        }, 404
    
    if current_user.id == user_id or current_user.is_admin:
        user_to_delete = db.session.scalar(
            db.select(User)
            .filter_by(id=user_id)
        )

        if user_to_delete:
            db.session.delete(user_to_delete)
            db.session.commit()
            return {
                "Message": f"User {user_to_delete.username} deleted successfully."
            }, 200
        else:
            return {
                "Error": f"Unable to find user with id {user_id}."
            }, 404
    else:
        return {
            "Error": "Not authorised to delete this user."
        }, 403
from datetime import timedelta

from flask import Blueprint, request
from flask_jwt_extended import create_access_token
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from psycopg2 import errorcodes

from init import db, bcrypt
from models.user import User, user_schema

user_bp = Blueprint('user', __name__, url_prefix='/user')


@user_bp.route("/register", methods=["POST"])
def user_register():
    try:
        body_data = request.get_json()
        user = User(
            username=body_data.get('username'),
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

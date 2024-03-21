# in built import
from datetime import timedelta
# external imports for requests, responses and validation
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_
from sqlalchemy.sql import func
from sqlalchemy.exc import IntegrityError
from psycopg2 import errorcodes
from werkzeug.security import generate_password_hash
# local imports for model, schemas, SQLAlchemy and bcrypt
from init import db, bcrypt
from models.user import User, user_schema, users_public_schema
from models.user import user_schema_partial, user_registration_schema
# blueprint definition for url endpoint
user_bp = Blueprint('user', __name__, url_prefix='/user')


# request to get all current users
@user_bp.route("/")
def get_all_users():
    # query database and fetch all users
    users = User.query.all()
    # serialise users into JSON objects based on schema
    result = users_public_schema.dump(users)
    # return result as a response with successful status code
    return jsonify({"users": result}), 200


# request to get all users from a specified location
@user_bp.route("/location")
def get_users_by_location():
    # retrieve the value of the location query parameter
    location = request.args.get('location')
    # check for a parameter value
    if not location:
        return jsonify(
            {
                "Error": "Location parameter is required"
            }
        ), 400
    # query database for user records based on location column
    users = User.query.filter(
        func.lower(User.location) == func.lower(location)
        ).all()
    if not users:
        # return 404 if no users found in search
        return jsonify(
            {
                "Error": f"No users found in {location}"
            }
        ), 404
    # return serialised JSON object based on schema
    return users_public_schema.dump(users), 200


# route to create user profiles as a POST request
@user_bp.route("/register", methods=["POST"])
def user_register():
    # retrieve the JSON data from the request
    body_data = request.get_json()

    try:
        # validate data against UserSchema
        errors = user_registration_schema.validate(body_data)
        # return schema error messages if data is not valid
        if errors:
            return jsonify(errors), 400
        # mandatory fields for JSON body data
        username = body_data.get('username')
        email = body_data.get('email')
        password = body_data.get('password')

        # create a User instance
        user = User(
            username=username,
            email=email,
            # location is an optional field
            location=body_data.get('location')
        )
        # use bcrypt to hash the password from the body data
        user.password = bcrypt.generate_password_hash(password).decode(
                'utf-8'
                )
        # add and commit record to database
        db.session.add(user)
        db.session.commit()
        # return schema as JSON object with created status code
        return user_schema.dump(user), 201
    # handle possible integrity errors
    except IntegrityError as err:
        # undo changes made in the session
        db.session.rollback()
        # extract error code from the exception
        error_code = err.orig.pgcode
        # check for not null violation in error code
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            # return error message with bad request status code
            return jsonify(
                {
                    "Error": f"The {err.orig.diag.column_name} field"
                    " is required to create a user."
                }
            ), 400
        # check for unique violation in error code
        if error_code == errorcodes.UNIQUE_VIOLATION:
            # define the violated unique constraint
            column_name = err.orig.diag.constraint_name
            # return specific JSON response based on unique violation
            if 'username' in column_name:
                return jsonify(
                    {
                        "Error": "That username is already taken."
                        " Please choose another one."
                    }
                ), 400
            if 'email' in column_name:
                return jsonify(
                    {
                        "Error": "That email is already registered."
                        " Please use a different email."
                    }
                ), 400


# POST request for user login
@user_bp.route("/login", methods=["POST"])
def user_login():
    # retrieve JSON data from request
    body_data = request.get_json()
    # retrive username or email from specified field
    login_field = body_data.get("username/email")
    # find username or email to match login_field
    stmt = db.select(User).filter(
        or_(User.email == login_field, User.username == login_field)
        )
    # execute query and store result in user variable
    user = db.session.scalar(stmt)
    # check for user and matching password
    if user and bcrypt.check_password_hash(
            user.password,
            body_data.get('password')
            ):
        # create JWT token for user with expiry set for 7 days
        token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(days=7)
            )
        # return user info with token as a JSON response
        return jsonify(
            {
                "username": user.username,
                "email": user.email, "token": token,
                "is_admin": user.is_admin
            }
        ), 200
    # return an error and unauthorised status code
    # in the case of invalid fields
    else:
        return jsonify(
            {
                "Error": "Username or password is invalid"
            }
        ), 401


# PATCH request for updating user info
@user_bp.route("/", methods=["PUT", "PATCH"])
# check for a valid JWT token
@jwt_required()
def edit_user():
    # retrieve user identity from JWT token
    current_user_id = get_jwt_identity()
    # query database for a user with matching ID
    current_user = User.query.filter_by(id=current_user_id).first()
    # if no user is found return error message with not found status code
    if not current_user:
        return jsonify(
            {
                "Error": "User could not be found."
            }
        ), 404
    # retrieve JSON data from request
    data = request.get_json()

    try:
        # request data against user_schema_partial
        errors = user_schema_partial.validate(data)
        # return bad request with error response in case of validation error
        if errors:
            return jsonify(errors), 400
        # update current_user value with fields provided in request data
        if 'username' in data:
            current_user.username = data['username']
        if 'email' in data:
            current_user.email = data['email']
        if 'location' in data:
            current_user.location = data['location']
        # hash new password before storing it within current_user
        if 'password' in data:
            current_user.password = generate_password_hash(data['password'])
        # commit the session
        db.session.commit()
        # return a message response if update is successful
        return jsonify(
            {
                "Messsage": "User updated successfully"
            }
        ), 200
    # handle integrity errors
    except IntegrityError as err:
        # undo changes in session
        db.session.rollback()
        # retrive error code from original exception
        error_code = err.orig.pgcode
        # check for unique violation in error code
        if error_code == errorcodes.UNIQUE_VIOLATION:
            # check for column where unique violation occured
            column_name = err.orig.diag.constraint_name
            # return error based on the field where the exception occured
            if 'username' in column_name:
                return jsonify(
                    {
                        "Error": "That username is already taken."
                        " Please choose another one."
                    }
                ), 400
            elif 'email' in column_name:
                return jsonify(
                    {
                        "Error": "That email is already registered."
                        " Please use a different email."
                    }
                ), 400


# DELETE request to handle removing user records
@user_bp.route("/<int:user_id>", methods=["DELETE"])
# check for valid JWT token
@jwt_required()
def delete_user(user_id):
    # get user identity from JWT token
    current_user_id = get_jwt_identity()
    # find user associated with current_user_id in database
    stmt = db.select(User).filter_by(id=current_user_id)
    # set query result as the value of current_user
    current_user = db.session.scalar(stmt)
    # return 404 error if no user is found
    if not current_user:
        return jsonify(
            {
                "Error": "User not found."
            }
        ), 404
    # check to see if the user has admin status
    # or matches the user to be deleted
    if current_user.id == user_id or current_user.is_admin:
        # query database for the id specified in the URL
        user_to_delete = db.session.scalar(
            db.select(User)
            .filter_by(id=user_id)
        )
        # if the id is found delete the user record and commit the session
        if user_to_delete:
            db.session.delete(user_to_delete)
            db.session.commit()
            # return a successful response confirming which user was deleted
            return jsonify(
                {
                    "Message": f"User {user_to_delete.username} deleted."
                }
            ), 200
        # return a not found error if no user matches the specified id
        else:
            return jsonify(
                {
                    "Error": f"Unable to find user with id {user_id}."
                }
            ), 404
    # return an error with a forbidden status code if the user is not authrised
    else:
        return jsonify(
            {
                "Error": "Not authorised to delete this user."
            }
        ), 403

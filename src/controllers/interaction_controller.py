# external imports for flask and SQLAlchemy
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from sqlalchemy import func, case
from sqlalchemy.exc import DataError, IntegrityError, NoResultFound
# local imports for SQLAlchemy, models and schemas
from init import db
from models.interaction import Interaction
from models.interaction import interactions_schema, interaction_schema
from models.user import User
from models.media import Media

# define blueprint for interaction URL endpoint
interaction_bp = Blueprint('interaction', __name__, url_prefix='/interaction')


# GET request to show fltered interactions of a specific user
@interaction_bp.route("/user", methods=["GET"])
# check for JWT token
@jwt_required()
def get_user_interactions():
    # query parameters for request filtering
    username = request.args.get('username')
    watched = request.args.get('watched')
    ratings = request.args.get('rating')
    watchlist = request.args.get('watchlist')
    # check to see if a username is provided
    if not username:
        # return a bad request if no username
        return jsonify(
            {
                "Error": "Username is required"
            }
        ), 400
    # query the database to search for a username that matches
    # the one prodided in the request
    user = User.query.filter_by(username=username).first()
    # return a not found error message if not matching user is found
    if not user:
        return jsonify(
            {
                "Error": f"User {username} not found"
            }
        ), 404
    # query the database for interaction records
    query = Interaction.query.filter_by(user_id=user.id)
    # apply filters to the query variable
    if watched == 'yes':
        query = query.filter_by(watched=watched)

    if watchlist == 'yes':
        query = query.filter_by(watchlist=watchlist)

    if ratings == 'yes':
        query = query.filter(Interaction.rating.isnot(None))
    # search for interactions matching the query filters
    interactions = query.all()
    # if no interactions are found return an error message
    # as a JSON response
    if not interactions:
        return jsonify(
            {
                "Error": f"No specified interactions found for '{username}'."
            }
        ), 404
    # return any interactions as a JSON response based on the schema
    return jsonify(interactions_schema.dump(interactions)), 200


# GET requestv to retrieve interactions on a
# specified media record
@interaction_bp.route("/media", methods=["GET"])
# check for valid JWT token
@jwt_required()
def get_media_interactions():
    # search parameters for query filters
    title = request.args.get('title')
    watched = request.args.get('watched')
    ratings = request.args.get('rating')
    watchlist = request.args.get('watchlist')
    # check to see if a title is provided
    if not title:
        # return bad request JSON response if no title
        return jsonify(
            {
                "Error": "Must enter a value for title."
            }
        ), 400
    # query the database for a media record with a matching title
    # to the search parameter
    media = Media.query.filter(
            func.lower(Media.title) == func.lower(title)
        ).first()
    if not media:
        return jsonify(
            {
                "Error": f"'{title}' could not be found."
            }
        ), 404
    # query the database for interaction record on
    # the media record found
    query = Interaction.query.filter_by(media_id=media.id)
    # apply filters to query variable from search parameters
    if watched == 'yes':
        query = query.filter_by(watched=watched)

    if watchlist == 'yes':
        query = query.filter_by(watchlist=watchlist)

    if ratings == 'yes':
        query = query.filter(Interaction.rating.isnot(None))
    # search for interactions matching specified filters
    interactions = query.all()
    # return a 404 JSON response if no interactions were found
    if not interactions:
        return jsonify(
            {
                "Error": f"No specified interactions found for '{title}'."
            }
        ), 404
    # return a JSON response with the matching interactions
    return jsonify(interactions_schema.dump(interactions)), 200


# GET request to retrieve total interactions on a media record
@interaction_bp.route("/summary", methods=["GET"])
def get_media_summary():
    # retrieve title query parameter
    title = request .args.get('title')
    if not title:
        # return a bad request response in no title provided
        return jsonify(
            {
                "Error": "Title parameter is required."
            }
        ), 400
    # query the database to find a media record matching title
    media = Media.query.filter(
        func.lower(Media.title) == func.lower(title)
        ).first()
    if not media:
        # return a not found response if no record is found
        return jsonify(
            {
                "Error": f"Title {title} not found."
            }
        ), 404
    # query database to aggregate interaction data
    summary = db.session.query(
        Media.title,
        Media.category,
        # use count to get the total number of watched, watchlist, ratings
        # use case for enum category differentiating
        func.count(case((Interaction.watched == 'yes', 1), else_=0)
                   ).label('watched_count'),
        func.count(Interaction.rating).label('rating_count'),
        # use avg to retrieve the average rating given by users
        func.avg(Interaction.rating).label('average_rating'),
        func.count(case((Interaction.watchlist == 'yes', 1), else_=0)
                   ).label('watchlist_count')
        ).join(
            Interaction
        ).filter(
            Interaction.media_id == media.id
        ).group_by(
            Media.id
        ).first()

    if not summary:
        # return a not found response if no interactions exist
        return jsonify(
            {
                "Error": f"No interactions found for {title}."
            }
        ), 404
    # convert summary data to dictionary for the response
    result = {
        "title": summary.title,
        "category": summary.category.value,
        "watched_count": summary.watched_count,
        "rating_count": summary.rating_count,
        "average_rating": float(summary.average_rating) if summary.average_rating else None,
        "watchlist_count": summary.watchlist_count
    }
    # return a JSON response for result
    return jsonify(result), 200


# POST and PATCH request for creating and updating interactions
# on media records specified by id in the URL
@interaction_bp.route("/<int:media_id>", methods=["POST", "PATCH"])
# check for a valid JWT token
@jwt_required()
def interaction(media_id):
    try:
        # get user identity from JWT token
        current_user_id = get_jwt_identity()
        # query the database to find the user
        user = User.query.get(current_user_id)
        # return 404 response if no user is found
        if not user:
            return jsonify(
                {
                    "Error": "User not found"
                }
            ), 404
        # query the database to find the id of the
        # media record specified in the URL
        media = Media.query.get(media_id)
        if not media:
            # return not found response if no matching record is found
            return jsonify(
                {
                    "Error": f"Media with id {media_id} could not be found"
                }
            ), 404
        # retrieve JSON data from request body
        body_data = request.get_json()
        # query the database to see if the user has
        # made an interaction record for this media
        existing = Interaction.query.filter_by(
            user_id=user.id, media_id=media.id
            ).first()
        
        try:
            # deserialise and validate body request
            interaction_schema.load(body_data)
        except ValidationError as err:
            return jsonify(err.messages), 400
        
        # check request method for POST
        if request.method == "POST":
            # return a bad request response if the user
            # already has an interaction for the media record
            if existing:
                return jsonify(
                    {
                        "Error": "Interaction already exists."
                        " Use PUT or PATCH to update."
                    }
                ), 400
            # if no interaction exists create a new instance
            # based on data found in the request body
            interaction = Interaction(
                watched=body_data.get('watched'),
                rating=body_data.get('rating'),
                watchlist=body_data.get('watchlist'),
                user=user,
                media=media
            )
            # add the instance to the database
            db.session.add(interaction)
            # else used for PATCH request
        else:
            # if no interaction record exists
            # return a not found response
            if not existing:
                return jsonify(
                    {
                        "Error": "No interaction found. Use POST to create."
                    }
                ), 404
            # if an interaction is found update it
            # using data found in the request body
            existing.watched = body_data.get('watched', existing.watched)
            existing.rating = body_data.get('rating', existing.rating)
            existing.watchlist = body_data.get('watchlist', existing.watchlist)
        # commit the session
        db.session.commit()
        # if existing return a successful response
        if existing:
            return jsonify(interaction_schema.dump(existing)), 200
        # if a new interaction record is created return a created status code
        else:
            return jsonify(interaction_schema.dump(interaction)), 201
    # handle potential data error
    except DataError:
        # undo changes in the session
        db.session.rollback()
        # return forbidden status code when enum constraint is violated
        return jsonify(
            {
                "Error": "Invalid value for watched or watchlist,"
                " must be either yes or no."
            }
        ), 422
    # handle potential integrity error
    except IntegrityError:
        # undo changes in the session
        db.session.rollback()
        # return forbidden response when rating is not an integer
        return jsonify(
            {
                "Error": "Rating can only be whole numbers from 0 to 10."
            }
        ), 422


# DELETE request to handle the removal of a specified interaction record
@interaction_bp.route("/<int:interaction_id>", methods=["DELETE"])
# check for valid JWT token
@jwt_required()
def delete_interaction(interaction_id):
    # retrieve user identity from JWT token
    current_user_id = get_jwt_identity()

    try:
        # find interaction by id
        # check that it belongs to the current user
        interaction_to_delete = db.session.scalar(
            db.select(Interaction)
            .join(User)
            .filter(
                Interaction.id == interaction_id,
                User.id == current_user_id
            )
        )
    # if the interaction is not found or belongs to another user
    # set value to none
    except NoResultFound:
        interaction_to_delete = None
    # if the result is None check the database to find the current user
    if not interaction_to_delete:
        current_user = db.session.scalar(
            db.select(User)
            .filter_by(id=current_user_id)
        )
        # check the current users admin status
        if current_user.is_admin:
            # if user is admin find the interaction
            # without filtering by user id
            interaction_to_delete = db.session.scalar(
                db.select(Interaction)
                .filter_by(id=interaction_id)
            )
            # if no interaction is found return a not found response
            if not interaction_to_delete:
                return jsonify(
                    {
                        "Error": f"Interaction id {interaction_id} not found."
                    }
                ), 404

        else:
            # if the user is not admin return a forbidden response
            return jsonify(
                {
                    "Error": "Not authorised to delete this interaction."
                }
            ), 403
    # delete the record and commit the session
    db.session.delete(interaction_to_delete)
    db.session.commit()
    # return a JSON response with a confirmation message
    return jsonify(
        {
            "Message": f"Interaction with id {interaction_id} deleted."
        }
    ), 200

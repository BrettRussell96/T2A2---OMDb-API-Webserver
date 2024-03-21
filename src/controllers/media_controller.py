# in built imports for environment variables, requests, and decorator functions
import os
import requests
import functools
# external flask and SQLAlchemy imports for requests, JSON, JWT
# and exceptions
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.sql import func
from sqlalchemy.exc import DataError
# local imports for SQLAlchemy, medels, and schemas
from init import db
from models.user import User
from models.media import Media, media_schema, medias_schema
from models.media import media_titles_schema, media_plots_schema
from models.media import media_ratings_schema

# blueprint for media URL endpoint
media_bp = Blueprint('media', __name__, url_prefix='/media')
# retrieves API key from .env variable
api_key = os.getenv('OMDB_API_KEY')


# wrapper function to check for admin status
def authorise_as_admin(fn):
    # decorator to preserve metadata
    @functools.wraps(fn)
    # *args **kwargs used to accept positional and keyword arguments
    def wrapper(*args, **kwargs):
        # get user identity from JWT token
        user_id = get_jwt_identity()
        # query database to select user
        stmt = db.select(User).filter_by(id=user_id)
        # store the query result as user value
        user = db.session.scalar(stmt)
        # check user for admin status
        if user.is_admin:
            # call the original function with its arguments
            return fn(*args, **kwargs)
        # return error message with forbidden
        # status code if the user is not admin
        else:
            return jsonify(
                {
                    "Error": "Only admin users can delete media."
                }
            ), 403

    return wrapper


# GET request to retrieve media records
@media_bp.route("/", methods=["GET"])
def get_media():
    # query parameters defined for filtering search results
    # as well as the table columns displayed in result
    info_type = request.args.get('info')
    media_type = request.args.get('media')
    genre = request.args.get('genre')
    actor = request.args.get('actor')
    director = request.args.get('director')
    # initialise query before filtering
    query = Media.query
    try:
        # check to see if series or movie is specified
        if media_type:
            # query the database to find records with matching category
            query = query.filter(Media.category == media_type)
        # check to see if genre is specified
        if genre:
            # query the database for genres matching the query parameter value
            filtered_query = query.filter(Media.genre.ilike(f"%{genre}%"))
            # if no matching genres are found return a 404 error message
            if filtered_query.first() is None:
                return jsonify(
                    {
                        "Error": f"Genre {genre} not found."
                    }
                ), 404
            # add filtered query value to query variable
            query = filtered_query
        # check to see if an actor is specified
        if actor:
            # query the database to find a matching actor
            filtered_query = query.filter(Media.actors.ilike(f"%{actor}%"))
            if filtered_query.first() is None:
                # return 404 error message if none is found
                return jsonify(
                    {
                        "Error": f"Actor {actor} not found."
                    }
                ), 404
            # apply filter to query
            query = filtered_query

        # check to see if a director is specified
        if director:
            # query database to find any matching director
            filtered_query = query.filter(
                    Media.director.ilike(f"%{director}%")
                )
            if filtered_query.first() is None:
                # return error message if none are found
                return jsonify(
                    {
                        "Error": f"Director {director} not found."
                    }
                ), 404
            # apply filter to query variable
            query = filtered_query
        # after all filters are applied
        # execute query to retrieve matching records
        media = query.all()
    # handle data errors
    except DataError:
        # return an error message with forbidden status code if
        # media value violates enum constraint
        return jsonify(
            {
                "Error": "Media must be either movie or series if specified."
            }
        ), 422
    # match case to determine displayed info
    # return JSON object with appropriate schema
    # based on info type parameter
    match info_type:
        case 'title':
            result = media_titles_schema.dump(media)
        case 'plot':
            result = media_plots_schema.dump(media)
        case 'rating':
            result = media_ratings_schema.dump(media)
        case 'all':
            result = medias_schema.dump(media)
            # returns forbidden status code if the info type
            # does not match one of the cases
        case _:
            return jsonify(
                {
                    "Error": "Invalid info type. Please specify either "
                    "title, plot, rating, or all"
                }
            ), 422
    # return JSON media record
    return jsonify({"media": result}), 200


# GET request for retrieving a single movie record
@media_bp.route("/movie", methods=["GET"])
@jwt_required()
def get_movie():
    # request parameter for a movie title
    title = request.args.get('title')
    # check to confirm a title is spcified in the request
    if not title:
        return jsonify(
            {
                "Error": "A title parameter is required"
            }
        ), 400
    # query the database to find a title matching the parameter
    movie = Media.query.filter(
            func.lower(Media.title) == func.lower(title),
            Media.category == 'movie'
        ).first()
    if movie:
        # return JSON response if a matching title is found
        return media_schema.dump(movie), 200
    # use API key to retrieve data if
    # the title is not found in the local database
    response = requests.get(
        f"http://www.omdbapi.com/?t={title}&type=movie&plot=full&apikey={api_key}"
        )
    # convert the response to JSON format and store in data variable
    data = response.json()
    # check to confirm that the record is a movie
    if data.get('Type') == 'series':
        return jsonify(
            {
                "Error": "This title corresponds to a TV series, not a movie."
            }
        ), 400

    if response.status_code == 200 and data.get('Response') != 'False':
        # convert JSON response and use to create a new
        # media instance
        data = response.json()
        movie = Media(
            title=data.get('Title'),
            year=data.get('Year'),
            category='movie',
            genre=data.get('Genre'),
            director=data.get('Director'),
            writer=data.get('Writer'),
            actors=data.get('Actors'),
            plot=data.get('Plot'),
            country=data.get('Country'),
            ratings=data.get('Ratings'),
            metascore=data.get('Metascore'),
            box_office=data.get('BoxOffice', 0)
        )
        # store the retrieved instance in the local database
        db.session.add(movie)
        db.session.commit()
        # return a JSON response
        return media_schema.dump(movie), 201
    # return a not found error message if the title could not be found
    else:
        return jsonify(
            {
                "Error": "Title could not be found"
            }
        ), 404


# GET route to retrieve a single tv series record
@media_bp.route("/tv", methods=["GET"])
@jwt_required()
def get_tv():
    # title search parameter
    title = request.args.get('title')
    # return bad request if no title provided in request
    if not title:
        return jsonify(
            {
                "Error": "A title parameter is required"
            }
        ), 400
    # query the local database for a media record matching the title
    media = Media.query.filter(
            func.lower(Media.title) == func.lower(title),
            Media.category == 'series'
        ).first()
    # if a record is found return a JSON response
    if media:
        return media_schema.dump(media), 200
    # if not local record is found use API key to retrieve
    # a third party record
    response = requests.get(
        f"http://www.omdbapi.com/?t={title}&type=series&plot=full&apikey={api_key}"
        )
    # convert third party record to JSON format
    data = response.json()
    # check to confirm the title is that of a tv series
    if data.get('Type') == 'movie':
        return jsonify(
            {
                "Error": "This title corresponds to a movie, not a TV series."
            }
        ), 400
    # if a record of a tv series is found
    if response.status_code == 200 and data.get('Response') != 'False':
        # create a new media instance from the OMDb record
        data = response.json()
        tv = Media(
            title=data.get('Title'),
            year=data.get('Year'),
            category='series',
            genre=data.get('Genre'),
            director=data.get('director'),
            writer=data.get('Writer'),
            actors=data.get('Actors'),
            plot=data.get('Plot'),
            country=data.get('Country'),
            ratings=data.get('Ratings'),
        )
        # save that instance to the local database
        db.session.add(tv)
        db.session.commit()
        # return the new record as a JSON response
        return media_schema.dump(tv), 201
    # return a 404 error if no record of the title could be found
    else:
        return jsonify(
            {
                "Error": "Title could not be found"
            }
        ), 404


# DELETE request for removal of media records
@media_bp.route("/<int:media_id>", methods=["DELETE"])
# check for a valid JWT token
@jwt_required()
# check identity for admin status
@authorise_as_admin
def delete_media(media_id):
    # query the database to select a media record
    stmt = db.select(Media).filter_by(id=media_id)
    # store query result as media_to_delete
    media_to_delete = db.session.scalar(stmt)
    # if a record is found delete it then commit the session
    if media_to_delete:
        db.session.delete(media_to_delete)
        db.session.commit()
        # return a confirmation message as a response
        return jsonify(
            {
                "Message": f"Media {media_to_delete.title} deleted."
            }
        ), 200
    else:
        # if no media record is found
        # return an error message as a JSON response
        return jsonify(
            {
                "Error": f"Media with id {media_id} not found"
            }
        ), 404

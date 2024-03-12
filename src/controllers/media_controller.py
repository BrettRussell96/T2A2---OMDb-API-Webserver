import os
import requests

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from init import db
from models.media import Media, media_schema, medias_schema
from models.media import media_titles_schema, media_plots_schema
from models.media import media_ratings_schema

media_bp = Blueprint('media', __name__, url_prefix='/media')
api_key = os.getenv('OMDB_API_KEY')


@media_bp.route("/", methods=["GET"])
def get_media():
    info_type = request.args.get('info')
    media_type = request.args.get('media', 'all')

    if media_type == 'all':
        media = Media.query
    else:
        media = Media.query.filter(Media.category == media_type)

    match info_type:
        case 'title':
            result = media_titles_schema.dump(media)
        case 'plot':
            result = media_plots_schema.dump(media)
        case 'rating':
            result = media_ratings_schema.dump(media)
        case 'info':
            result = medias_schema.dump(media)
        case _:
            return {
                "Error": "Invalid query parameter"
                }, 400
    return {"media": result}, 200


@media_bp.route("/movie", methods=["GET"])
def get_movie():
    title = request.args.get('title')
    if not title:
        return {
            "Error": "A title parameter is required"
        }, 400

    movie = Media.query.filter_by(title=title).first()
    if movie:
        return media_schema.dump(movie)
    
    response = requests.get(
        f"http://www.omdbapi.com/?t={title}&type=movie&plot=full&apikey={api_key}"
        )
    data = response.json()

    if data.get('Type') == 'series':
        return {
            "Error": "This title corresponds to a TV series, not a movie."
        }, 400
    if response.status_code == 200 and data.get('Response') != 'False':
    
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

        db.session.add(movie)
        db.session.commit()
        return media_schema.dump(movie), 201
    
    else:
        return {
            "Error": "Title could not be found"
        }, 404


@media_bp.route("/tv", methods=["GET"])
def get_tv():
    title = request.args.get('title')
    if not title:
        return {
            "Error": "A title parameter is required"
        }, 400
    
    tv = Media.query.filter_by(title=title).first()
    if tv:
        return media_schema.dump(tv)
    
    response = requests.get(
        f"http://www.omdbapi.com/?t={title}&type=series&plot=full&apikey={api_key}"
        )
    data = response.json()

    if data.get('Type') == 'movie':
        return {
            "Error": "This title corresponds to a movie, not a TV series."
        }, 400
    
    if response.status_code == 200 and data.get('Response') != 'False':

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

        db.session.add(tv)
        db.session.commit()
        return media_schema.dump(tv), 201
    
    else:
        return {
            "Error": "Title could not be found"
        }, 404
    




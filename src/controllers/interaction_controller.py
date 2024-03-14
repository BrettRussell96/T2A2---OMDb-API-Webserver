import functools

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from sqlalchemy.exc import DataError, IntegrityError, NoResultFound

from init import db
from models.interaction import Interaction
from models.interaction import interactions_schema, interaction_schema
from models.user import User
from models.media import Media

interaction_bp = Blueprint('interaction', __name__, url_prefix='/interaction')


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


@interaction_bp.route("/user", methods=["GET"])
@jwt_required()
def get_user_interactions():
    username = request.args.get('username')
    watched = request.args.get('watched')
    ratings = request.args.get('rating')
    watchlist = request.args.get('watchlist')

    if not username:
        return {
            "Error": "Username is required"
        }, 400
    
    user = User.query.filter_by(username=username).first()
    if not user:
        return {
            "Error": f"User {username} not found"
        }, 404
    
    query = Interaction.query.filter_by(user_id=user.id)

    if watched == 'yes':
        query = query.filter_by(watched=watched)

    if watchlist == 'yes':
        query = query.filter_by(watchlist=watchlist)

    if ratings == 'yes':
        query = query.filter(Interaction.rating.isnot(None))
    
    interactions = query.all()
    if not interactions:
        return {
            "Error": f"No specified interactions found for user '{username}'."
        }, 404

    return jsonify(interactions_schema.dump(interactions)), 200


@interaction_bp.route("/media", methods=["GET"])
@jwt_required()
def get_media_interactions():
    title = request.args.get('title')
    watched = request.args.get('watched')
    ratings = request.args.get('rating')
    watchlist = request.args.get('watchlist')

    if not title:
        return {
            "Error": "Must enter a value for title."
        }, 400

    media = Media.query.filter(func.lower(Media.title) == func.lower(title)).first()
    if not media:
        return {
            "Error": f"'{title}' could not be found."
        }, 404
    
    query = Interaction.query.filter_by(media_id=media.id)
    if watched == 'yes':
        query = query.filter_by(watched=watched)
    
    if watchlist == 'yes':
        query = query.filter_by(watchlist=watchlist)
    
    if ratings == 'yes':
        query = query.filter(Interaction.rating.isnot(None))
    
    interactions = query.all()
    if not interactions:
        return {
            "Error": f"No specified interactions found for media '{title}'."
        }, 404
    
    return jsonify(interactions_schema.dump(interactions)), 200


@interaction_bp.route("/<int:media_id>", methods=["POST", "PATCH"])
@jwt_required()
def interaction(media_id):
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user:
            return {
                "Error": "User not found"
            }, 404

        media = Media.query.get(media_id)
        if not media:
            return {
                "Error": f"Media with id {media_id} could not be found"
            }, 404
        
        body_data = request.get_json()

        existing = Interaction.query.filter_by(
            user_id=user.id, media_id=media.id
            ).first()

        if request.method == "POST":
            if existing:
                return {
                    "Error": "Interaction already exists."
                    " Use PUT or PATCH to update."
                }, 400
            interaction = Interaction(
                watched=body_data.get('watched'),
                rating=body_data.get('rating'),
                watchlist=body_data.get('watchlist'),
                user=user,
                media=media
            )
            db.session.add(interaction)
        else:
            if not existing:
                return {
                    "Error": "No interaction found. Use POST to create." 
                }, 404
            existing.watched = body_data.get('watched', existing.watched)
            existing.rating = body_data.get('rating', existing.rating)
            existing.watchlist = body_data.get('watchlist', existing.watchlist)
        
        db.session.commit()
        if existing:
            return jsonify(interaction_schema.dump(existing)), 200 
        else:
            return jsonify(interaction_schema.dump(interaction)), 201
    
    except DataError:
        db.session.rollback()
        return {
            "Error": "Invalid value for watched or watchlist," 
            " must be either yes or no."
        }, 422
    except IntegrityError:
        db.session.rollback()
        return {
            "Error": "Rating can only be whole numbers from 0 to 10."
        }, 422


@interaction_bp.route("/<int:interaction_id>", methods=["DELETE"])
@jwt_required()
def delete_interaction(interaction_id):
    current_user_id = get_jwt_identity()

    try:
        interaction_to_delete = db.session.scalar(
            db.select(Interaction)
            .join(User)
            .filter(Interaction.id == interaction_id, User.id == current_user_id)
        )
    except NoResultFound:
        interaction_to_delete = None

    if not interaction_to_delete:
        current_user = db.session.scalar(db.select(User).filter_by(id=current_user_id))
        if current_user.is_admin:
            interaction_to_delete = db.session.scalar(
                db.select(Interaction)
                .filter_by(id=interaction_id)
            ) 
            if not interaction_to_delete:
                return {
                    "Error": f"Unable to find interaction with id {interaction_id}."
                }, 404
        else:
            return {
                "Error": "Not authorised to delete this interaction."
            }, 403
    
    db.session.delete(interaction_to_delete)
    db.session.commit()
    return {
        "Message": f"Interaction with id {interaction_id} deleted successfully."
    }


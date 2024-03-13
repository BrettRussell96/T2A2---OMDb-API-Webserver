from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from init import db
from models.interaction import Interaction
from models.interaction import interactions_schema, interaction_schema
from models.user import User
from models.media import Media

interaction_bp = Blueprint('interaction', __name__, url_prefix='/interaciton')


@interaction_bp.route("/media/<int:media_id>", methods=["POST"])
@jwt_required()
def interaction(media_id):

    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return {
            "Error": "User not found"
        }, 404

    media = media.query.get(media_id)
    if not media:
        return {
            "Error": f"Media with id {media_id} could not be found"
        }, 404
    
    body_data = request.get_json()

    watched = body_data.get('watched')
    if not watched:
        return {
            "Error": "Watched value can only be yes or no."
        }, 400
    
    rating = body_data.get('rating')
    if not rating:
        return {
            "Error": "Rating must be a whole number from 0-10."
        }, 400
    
    watchlist = body_data.get('watchlist')
    if not watchlist:
        return {
            "Error": "Watchlist value can only be yes or no."
        }, 400

    interaction = Interaction(
        watched=watched,
        rating=rating,
        watchlist=watchlist,
        user=user,
        media=media
    )

    db.session.add(interaction)
    db.session.commit()

    return jsonify(interaction_schema.dump(interaction))
    

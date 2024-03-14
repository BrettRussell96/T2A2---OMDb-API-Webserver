from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import DataError, IntegrityError

from init import db
from models.interaction import Interaction
from models.interaction import interactions_schema, interaction_schema
from models.user import User
from models.media import Media

interaction_bp = Blueprint('interaction', __name__, url_prefix='/interaction')


@interaction_bp.route("/media/<int:media_id>", methods=["POST"])
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

        interaction = Interaction(
            watched=body_data.get('watched'),
            rating=body_data.get('rating'),
            watchlist=body_data.get('watchlist'),
            user=user,
            media=media
        )

        db.session.add(interaction)
        db.session.commit()
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
    

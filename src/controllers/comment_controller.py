from datetime import date
import functools

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm.exc import NoResultFound

from init import db
from models.comment import Comment, comment_schema, comments_schema
from models.user import User
from models.media import Media, MediaEnum

comment_bp = Blueprint('comment', __name__, url_prefix='/comment')


@comment_bp.route("/create", methods=["POST"])
@jwt_required()
def create_comment():
    current_user_id = get_jwt_identity()

    data = request.get_json()

    if 'title' not in data or 'category' not in data or 'content' not in data:
        return {
            "Error": "title, category, and content are required."
        }, 400
    
    title = data['title']
    category = data['category']
    content = data['content']
    parent_id = data.get('parent_id')

    try:
        category_enum = MediaEnum[category]
        media = Media.query.filter_by(title=title, category=category_enum).one()
    except NoResultFound:
        return {
            "Error": "Media not found."
        },404
    except KeyError:
        return {
            "Error": "Category value must be either 'movie' or 'series'."
        }, 500
    
    new_comment = Comment(
        content=content,
        user_id=current_user_id,
        media_id=media.id,
        parent_id=parent_id
    )

    db.session.add(new_comment)
    db.session.commit()

    return jsonify(comment_schema.dump(new_comment)), 201



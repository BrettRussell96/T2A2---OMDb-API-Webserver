from datetime import date

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm.exc import NoResultFound

from init import db
from models.comment import Comment, comment_schema, comments_schema
from models.user import User
from models.media import Media, MediaEnum


comment_bp = Blueprint('comment', __name__, url_prefix='/comment')


@comment_bp.route("/", methods=["GET"])
def get_comments():
    username = request.args.get('username')
    title = request.args.get('title')
    query = db.session.query(Comment)

    if username:
        query = query.join(User).filter(User.username == username)
    
    if title:
        query = query.join(Media).filter(Media.title.ilike(title))
    
    comments = query.all()

    if not comments:
        return jsonify(
            {
                "Error": "No comments found matching the criteria."
            }
        ), 404
    
    return jsonify(comments_schema.dump(comments)), 200


@comment_bp.route("/create", methods=["POST"])
@jwt_required()
def create_comment():
    current_user_id = get_jwt_identity()

    data = request.get_json()

    if 'title' not in data or 'category' not in data or 'content' not in data:
        return jsonify(
            {
                "Error": "title, category, and content are required."
            }
        ), 400
    
    title = data['title']
    category = data['category']
    content = data['content']
    parent_id = data.get('parent_id')

    try:
        category_enum = MediaEnum[category]
        media = Media.query.filter_by(title=title, category=category_enum).one()
    except NoResultFound:
        return jsonify(
            {
                "Error": "Media not found."
            }
        ), 404
    except KeyError:
        return jsonify(
            {
                "Error": "Category value must be either 'movie' or 'series'."
            }
        ), 500
    
    new_comment = Comment(
        content=content,
        user_id=current_user_id,
        media_id=media.id,
        parent_id=parent_id
    )

    db.session.add(new_comment)
    db.session.commit()

    return jsonify(comment_schema.dump(new_comment)), 201


@comment_bp.route("/<int:comment_id>", methods=["PATCH"])
@jwt_required()
def update_comment(comment_id):
    current_user_id = int(get_jwt_identity())

    comment = Comment.query.get(comment_id)

    if not comment:
        return jsonify(
            {
                "Error": "Comment not found."
            }
        ), 404
        

    if comment.user_id != current_user_id:
        return jsonify(
            {
                "Error": "You are not authorised to update this comment."
            }
        ), 403
    
    data = request.get_json()
    new_content = data.get('content')

    if not new_content:
        return jsonify(
            {
                "Error": "Content is required."
            }
        ), 400
    
    comment.content = new_content
    db.session.commit()
    return jsonify(comment_schema.dump(comment)), 200


@comment_bp.route("/<int:comment_id>", methods=["DELETE"])
@jwt_required()
def delete_comment(comment_id):
    current_user_id = get_jwt_identity()

    try:
        comment_to_delete = db.session.scalar(
            db.select(Comment)
            .join(User)
            .filter(Comment.id == comment_id, User.id == current_user_id)
        )
    except NoResultFound:
        comment_to_delete = None

    if not comment_to_delete:
        current_user = db.session.scalar(
            db.select(User)
            .filter_by(id=current_user_id)
        )
        if current_user.is_admin:
            comment_to_delete = db.session.scalar(
                db.select(Comment)
                .filter_by(id=comment_id)
            )
            if not comment_to_delete:
                return jsonify(
                    {
                        "Error": f"Unable to find comment with id {comment_id}."
                    }
                ), 404
        else:
            return jsonify(
                {
                    "Error": "Not authorised to delete this comment."
                }
            ), 403
    
    db.session.delete(comment_to_delete)
    db.session.commit()
    return jsonify(
        {
            "Message": f"Comment with id {comment_id} deleted successfully."
        }
    ), 200




from collections import defaultdict
# external imports for flask and SQLAlchemy
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
# from sqlalchemy import or_
from sqlalchemy.sql import func
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound
# local imports for SQLAlchemy, models and schemas
from init import db
from models.comment import Comment, comment_schema
from models.user import User
from models.media import Media, MediaEnum

# define a blueprint for comment URL endpoint
comment_bp = Blueprint('comment', __name__, url_prefix='/comment')


# GET route to view comments made for any media
# or by any user
@comment_bp.route("/", methods=["GET"])
def get_comments():
    # retrieve query parameters
    username = request.args.get('username')
    title = request.args.get('title')
    # initialise query to fetch comments
    # with related child comments
    query = Comment.query.options(
        joinedload(Comment.user),
        joinedload(Comment.media),
        joinedload(Comment.children)
    )
    # check for username parameter
    if username:
        # query database to find the user
        user = User.query.filter_by(username=username).first()
        # return a not found response if no user is found
        if not user:
            return jsonify(
                {
                    "Error": f"Username {username} not found."
                }
            ), 404
        # query database to find comments made by the user
        filtered_query = query.join(
                Comment.user
            ).filter(
                User.username == username
            )
        # return not found response if no result is found
        if filtered_query.first() is None:
            return jsonify(
                {
                    "Error": f"No comments found from user {username}."
                }
            ), 404
        # apply filter to query
        query = filtered_query
    # check for title parameter
    if title:
        # find title in the database
        media = Media.query.filter(
                func.lower(Media.title) == func.lower(title)
            ).first()
        # return not found error if not in the database
        if not media:
            return jsonify(
                {
                    "Error": f"Title {title} not found."
                }
            ), 404
        # search database for comments from the title
        filtered_query = query.join(
                Comment.media
            ).filter(
                func.lower(Media.title) == func.lower(title)
            )
        # return error if no comments are found
        if filtered_query.first() is None:
            return jsonify(
                {
                    "Error": f"No comments found for {title}."
                }
            ), 404
        # apply filter
        query = filtered_query
    # apply filtered search value to comments
    comments = query.all()
    # organise into a dictionary to make
    # parent comment id a key with child comments being value
    comments_by_parent = defaultdict(list)
    for comment in comments:
        comments_by_parent[comment.parent_id].append(comment)

    # nested recursive function used to serialise child comments
    def serialise_comment(comment):
        return {
            # media record values are stored in the key value pairs
            "id": comment.id,
            "content": comment.content,
            "created": comment.created.strftime("%Y-%m-%d T%H:%M"),
            "user": {
                "username": comment.user.username
                },
            "media": {
                "title": comment.media.title,
                "category": comment.media.category.name
                },
            # runs function recursively for each child comment
            "children": [
                serialise_comment(child) for child in comments_by_parent[
                    comment.id
                    ]
                ]
        }
    # top level comments are serialised using recursive function
    # this keeps replies nested within original comments
    serialised_comments = [
        serialise_comment(c) for c in comments if c.parent_id is None
        ]
    # return JSON response
    return jsonify(serialised_comments)


# POST route to create new comments
@comment_bp.route("/create", methods=["POST"])
# check for valid JWT
@jwt_required()
def create_comment():
    # get user id from JWT token
    current_user_id = get_jwt_identity()
    # extract JSON data from the request body
    data = request.get_json()
    # check for title, catagory and content in request body
    if 'title' not in data or 'category' not in data or 'content' not in data:
        # return bad request error message if either field is left empty
        return jsonify(
            {
                "Error": "title, category, and content are required."
            }
        ), 400
    # assign values from body data
    title = data['title']
    category = data['category']
    content = data['content']
    # parent_id is an optional value
    parent_id = data.get('parent id')

    try:
        # check for media matching title and category
        category_enum = MediaEnum[category]
        media = Media.query.filter(
                func.lower(Media.title) == func.lower(title)
            ).filter(
                Media.category == category_enum
            ).one()
        # Return 404 error message when no media is found
    except NoResultFound:
        return jsonify(
            {
                "Error": "Media not found."
            }
        ), 404
        # return 422 error message when the enum constraint is violated
    except KeyError:
        return jsonify(
            {
                "Error": "Category value must be either 'movie' or 'series'."
            }
        ), 422
    # create new comment instance
    new_comment = Comment(
        content=content,
        user_id=current_user_id,
        media_id=media.id,
        parent_id=parent_id
    )
    # add the instance to the database and commit
    db.session.add(new_comment)
    db.session.commit()
    # return a JSON response with the created comment record
    return jsonify(comment_schema.dump(new_comment)), 201


# PATCH request for updating existing comments
@comment_bp.route("/<int:comment_id>", methods=["PATCH"])
# check for valid JWT token
@jwt_required()
def update_comment(comment_id):
    # get user id from JWT token convert to int
    # to check against comment.user_id
    current_user_id = int(get_jwt_identity())
    # search database for comment to match the URL ID
    comment = Comment.query.get(comment_id)
    # return 404 error message if no comment found
    if not comment:
        return jsonify(
            {
                "Error": "Comment not found."
            }
        ), 404

    # check for authorisation return 403 forbidden if not authorised
    if comment.user_id != current_user_id:
        return jsonify(
            {
                "Error": "You are not authorised to update this comment."
            }
        ), 403
    # extract JSON data from request body
    data = request.get_json()
    new_content = data.get('content')
    # return 400 bad request if content field is empty
    if not new_content:
        return jsonify(
            {
                "Error": "Content is required."
            }
        ), 400
    # update the value of the comment column and commit
    comment.content = new_content
    db.session.commit()
    result = comment_schema.dump(comment)
    # return JSON response showing the updated comment
    return jsonify({"updated comment": result}), 200


# DELETE request for removing comments
@comment_bp.route("/<int:comment_id>", methods=["DELETE"])
# check for valid JWT TOKEN
@jwt_required()
def delete_comment(comment_id):
    # get user id from JWT token
    current_user_id = get_jwt_identity()

    try:
        # search for a comment with the URL id belonging to the current user
        comment_to_delete = db.session.scalar(
            db.select(Comment)
            .join(User)
            .filter(Comment.id == comment_id, User.id == current_user_id)
        )
        # return none if no match is found
    except NoResultFound:
        comment_to_delete = None

    if not comment_to_delete:
        # check database for user admin status
        current_user = db.session.scalar(
            db.select(User)
            .filter_by(id=current_user_id)
        )
        if current_user.is_admin:
            # if the user is admin search the database for
            # a comment with the specified id
            comment_to_delete = db.session.scalar(
                db.select(Comment)
                .filter_by(id=comment_id)
            )
            # return not found response if no comment is found
            if not comment_to_delete:
                return jsonify(
                    {
                        "Error": f"Cannot find comment with id {comment_id}."
                    }
                ), 404
        else:
            # return a 403 error message if the user does not
            # have admin status
            return jsonify(
                {
                    "Error": "Not authorised to delete this comment."
                }
            ), 403
    # delete the comment and commit the session
    db.session.delete(comment_to_delete)
    db.session.commit()
    # return a JSON confirmation response
    return jsonify(
        {
            "Message": f"Comment with id {comment_id} deleted successfully."
        }
    ), 200

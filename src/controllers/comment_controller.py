from datetime import date
import functools

from flask import Blueprint, request

from init import db
from models.comment import Comment, comment_schema, comments_schema
from models.user import User
from models.media import Media

comment_bp = Blueprint('comment', __name__, url_prefix='/comment')





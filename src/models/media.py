import enum

from sqlalchemy import Enum
from sqlalchemy.dialects.postgresql import JSONB
from marshmallow_enum import EnumField

from init import db, ma


class CategoryEnum(enum.Enum):
    movie = "movie"
    tv_show = "series"


class Media(db.Model):
    __tablename__ = "media"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    year = db.Column(db.String)
    category = db.Column(Enum(CategoryEnum))
    genre = db.Column(db.String)
    director = db.Column(db.String)
    writer = db.Column(db.String)
    actors = db.Column(db.String)
    plot = db.Column(db.Text)
    country = db.Column(db.String)
    ratings = db.Column(JSONB)
    metascore = db.Column(db.String)
    box_office = db.Column(db.String)


class MediaSchema(ma.Schema):
    category = EnumField(CategoryEnum, by_value=True)

    class Meta:
        model = Media
        fields = (
            'id',
            'title',
            'year',
            'category',
            'genre',
            'director',
            'writer',
            'actors',
            'plot',
            'country',
            'ratings',
            'metascore',
            'box_office'
        )
        ordered = True


media_schema = MediaSchema()
medias_schema = MediaSchema(many=True)
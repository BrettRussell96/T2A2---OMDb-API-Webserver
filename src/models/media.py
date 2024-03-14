import enum

from sqlalchemy import Enum
from sqlalchemy.dialects.postgresql import JSONB
from marshmallow import fields
from marshmallow_enum import EnumField

from init import db, ma


class MediaEnum(enum.Enum):
    movie = "movie"
    series = "series"


class Media(db.Model):
    __tablename__ = "media"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    year = db.Column(db.String)
    category = db.Column(Enum(MediaEnum))
    genre = db.Column(db.String)
    director = db.Column(db.String)
    writer = db.Column(db.String)
    actors = db.Column(db.String)
    plot = db.Column(db.Text)
    country = db.Column(db.String)
    ratings = db.Column(JSONB)
    metascore = db.Column(db.String)
    box_office = db.Column(db.String)

    interactions = db.relationship(
        'Interaction',
        back_populates='media'
    )


class MediaSchema(ma.Schema):

    id = fields.Int()
    title = fields.Str()
    year = fields.Str()
    category = EnumField(MediaEnum, by_value=True)

    class Meta:
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


class MediaTitleSchema(ma.Schema):
    category = EnumField(MediaEnum, by_value=True)
    class Meta:
        fields = (
            'id',
            'title',
            'category'
        )


media_titles_schema = MediaTitleSchema(many=True)


class MediaPlotSchema(ma.Schema):
    category = EnumField(MediaEnum, by_value=True)
    class Meta:
        fields = (
            'id',
            'title',
            'year',
            'category',
            'plot'
        )


media_plots_schema = MediaPlotSchema(many=True)


class MediaRatingSchema(ma.Schema):
    category = EnumField(MediaEnum, by_value=True)
    class Meta:
        fields = (
            'id',
            'title',
            'year',
            'category',
            'ratings',
            'metascore'
        )


media_ratings_schema = MediaRatingSchema(many=True)
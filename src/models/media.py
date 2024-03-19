# built in import for enum categories
import enum
# ecternal imports for JSONB, enum and schemas
from sqlalchemy import Enum
from sqlalchemy.dialects.postgresql import JSONB
from marshmallow import fields
from marshmallow_enum import EnumField
# local imports for SQLAlchemy and marshmallow
from init import db, ma

# class to define enum categories 
class MediaEnum(enum.Enum):
    movie = "movie"
    series = "series"

# create media model
class Media(db.Model):
    # set tablename to media
    __tablename__ = "media"
    # use db to define columns and datatypes
    # set id to primary key 
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    year = db.Column(db.String)
    # set category to enum type 
    category = db.Column(Enum(MediaEnum))
    genre = db.Column(db.String)
    director = db.Column(db.String)
    writer = db.Column(db.String)
    actors = db.Column(db.String)
    plot = db.Column(db.Text)
    country = db.Column(db.String)
    # set ratings to JSONB to store ratings from multiple sources
    ratings = db.Column(JSONB)
    metascore = db.Column(db.String)
    box_office = db.Column(db.String)
    # establish relationship between media and interaction
    interactions = db.relationship(
        'Interaction',
        back_populates='media'
    )

# create schema class
class MediaSchema(ma.Schema):
    # define data type for fields
    id = fields.Int()
    title = fields.Str()
    year = fields.Str()
    category = EnumField(MediaEnum, by_value=True)
    # class to specify fields included in serialised representation
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
        # specify correct order
        ordered = True

# schema instances to handle single and multiple record response
media_schema = MediaSchema()
medias_schema = MediaSchema(many=True)

# schema for showing condensed data
class MediaTitleSchema(ma.Schema):
    category = EnumField(MediaEnum, by_value=True)
    class Meta:
        fields = (
            'id',
            'title',
            'category'
        )

# instance for media title schema
media_titles_schema = MediaTitleSchema(many=True)

# schema for additional condensed data 
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

# schema to show ratings in response with condensed fields
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
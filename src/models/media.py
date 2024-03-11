import enum

from sqlalchemy import Enum

from init import db, ma


class CategoryEnum(enum.Enum):
    movie = "Movie"
    tv_show = "TV Show"


class Media(db.Model):
    __tablename__ = "media"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer)
    category = db.Column(Enum(CategoryEnum))
    genre = db.Column(db.String)
    director = db.Column(db.String)
    writer = db.Column(db.String)
    actors = db.Column(db.String)
    plot = db.Column(db.Text)
    country = db.Column(db.String)
    ratings = db.Column(db.String)
    metascore = db.Column(db.Integer)
    box_office = db.column(db.Integer)


class MediaSchema(ma.Schema):

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


media_schema = MediaSchema()
medias_schema = MediaSchema(many=True)
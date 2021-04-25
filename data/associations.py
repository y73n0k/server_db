import sqlalchemy

from .db_session import SqlAlchemyBase


video_to_authors = sqlalchemy.Table(
    "video_to_authors",
    SqlAlchemyBase.metadata,
    sqlalchemy.Column(
        "videos_id",
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("videos.id"),
    ),
    sqlalchemy.Column(
        "users_id",
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("users.id"),
    ),
)

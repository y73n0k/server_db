import datetime
import sqlalchemy

from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Comment(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "comments"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    created_date = sqlalchemy.Column(
        sqlalchemy.DateTime, default=datetime.datetime.now()
    )
    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    author = orm.relation("User")
    video_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("videos.id"), index=True
    )
    video = orm.relation("Video", backref="comments", lazy=True)
    reply_to = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey("comments.id"), nullable=True
    )

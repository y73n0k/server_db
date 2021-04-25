import datetime
import sqlalchemy

from base64 import urlsafe_b64encode as b64_enc
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from uuid import uuid4

from .db_session import SqlAlchemyBase


class Video(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "videos"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    short_name = sqlalchemy.Column(
        sqlalchemy.String,
        index=True,
    )
    description = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    ext = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    upload_date = sqlalchemy.Column(
        sqlalchemy.DateTime, default=datetime.datetime.now()
    )
    authors = orm.relation(
        "User",
        secondary="video_to_authors",
        lazy="subquery",
        backref=orm.backref("videos", lazy=True),
    )

    def set_short_name(self):
        self.short_name = b64_enc(uuid4().bytes).rstrip(b"=").decode("ascii")
        return self.short_name

from flask import jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from flask_restful import Resource, abort
from sqlalchemy.exc import IntegrityError

from data.users import User
from data import db_session

from .user_parser import parser


def abort_if_not_found(slug):
    session = db_session.create_session()
    user = session.query(User).filter(User.slug == slug).first()
    if user is None:
        abort(404, message="User not founded")


class UserResource(Resource):
    def get(self, slug):
        abort_if_not_found(slug)
        session = db_session.create_session()
        user = session.query(User).filter(User.slug == slug).first()
        videos = []
        for video in user.videos:
            videos.append(
                {
                    "short_name": video.short_name,
                    "title": video.title,
                    "description": video.description,
                    "upload_date": video.upload_date,
                }
            )
        answer = {"user": user.to_dict(only=("id", "name", "slug"))}
        answer["user"]["videos"] = videos
        return jsonify(answer)

    @jwt_required()
    def delete(self, slug):
        current_user_slug = get_jwt_identity()
        if current_user_slug == slug:
            return jsonify({"msg": "You cannot delete not your profile"})
        abort_if_not_found(slug)
        session = db_session.create_session()
        user = session.query(User).filter(User.slug == slug).first()
        session.delete(user)
        session.commit()
        return jsonify({"success": "OK"})

    @jwt_required()
    def put(self, slug):
        abort_if_not_found(slug)
        session = db_session.create_session()
        user_to_change = session.query(User).filter(User.slug == slug).first()
        current_user_id = get_jwt_identity()
        current_user = session.query(User).get(current_user_id)
        if current_user is None:
            abort(403, message="Token is wrong")
        if current_user != user_to_change:
            return jsonify({"msg": "You cannot change not your profile"})
        args = parser.parse_args()
        user_to_change.name = args["name"]
        user_to_change.slug = args["slug"]
        user_to_change.set_password(args["password"])
        try:
            session.commit()
            return jsonify({"success": "OK"})
        except IntegrityError as e:
            print(e)
            abort(409, message="This slug already exists")


class UserListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify(
            {"users": [item.to_dict(only=("id", "name", "slug")) for item in users]}
        )

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        user = User(
            name=args["name"],
            slug=args["slug"],
        )
        user.set_password(args["password"])
        session.add(user)
        try:
            session.commit()
            access_token = create_access_token(user.id)
            refresh_token = create_refresh_token(user.id)
            return jsonify(
                {
                    "success": "OK",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                }
            )
        except IntegrityError as e:
            print(e)
            abort(409, message="This slug already exists")

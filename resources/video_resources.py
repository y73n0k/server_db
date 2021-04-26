import os
import requests

from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, abort
from werkzeug.utils import secure_filename

from data import db_session
from data.users import User
from data.videos import Video

from .video_parser import parser
from init_app import PORT


ALLOWED_EXT = {"mp4", "webm"}


def abort_if_not_found(short_name):
    session = db_session.create_session()
    video = session.query(Video).filter(Video.short_name == short_name).first()
    if video is None:
        abort(404, message="Video not founded")


class VideoResource(Resource):
    def get(self, short_name):
        abort_if_not_found(short_name)
        session = db_session.create_session()
        video = session.query(Video).filter(Video.short_name == short_name).first()
        answer = {
            "video": video.to_dict(
                only=("id", "title", "short_name", "upload_date", "description")
            )
        }
        video_url = "/storage/" + video.short_name
        answer["video"]["url"] = video_url + "." + video.ext
        answer["video"]["authors"] = []
        for author in video.authors:
            answer["video"]["authors"].append(
                author.to_dict(only=("id", "name", "slug"))
            )
        answer["video"]["comments"] = []
        for comment in video.comments:
            data = requests.get(
                f"http://127.0.0.1:{PORT}/comments/" + str(comment.id)
            ).json()["comment"]
            answer["video"]["comments"].append(data)
        return jsonify(answer)

    @jwt_required()
    def delete(self, short_name):
        abort_if_not_found(short_name)
        current_user_id = get_jwt_identity()
        session = db_session.create_session()
        video = session.query(Video).filter(Video.short_name == short_name).first()
        current_user = session.query(User).get(current_user_id)
        if current_user is None:
            abort(403, message="Token is wrong")
        if current_user in video.authors:
            os.remove("storage/" + video.short_name + "." + video.ext)
            session.delete(video)
            session.commit()
            return jsonify({"success": "OK"})
        return jsonify({"msg": "You cannot delete not your video"})

    @jwt_required()
    def put(self, short_name):
        args = parser.parse_args()
        abort_if_not_found(short_name)
        current_user_id = get_jwt_identity()
        session = db_session.create_session()
        video = session.query(Video).filter(Video.short_name == short_name).first()
        current_user = session.query(User).get(current_user_id)
        if current_user is None:
            abort(403, message="Token is wrong")
        if current_user in video.authors:
            video.title = args["titles"]
            session.commit()
            return jsonify({"success": "OK"})
        return jsonify({"msg": "You cannot change not your video"})


class VideoListResource(Resource):
    def get(self):
        session = db_session.create_session()
        video = session.query(Video).all()
        answer = {"videos": []}
        for item in video:
            temp = item.to_dict(
                only=("id", "title", "short_name", "upload_date", "description")
            )
            temp["authors"] = [
                author.to_dict(only=("slug",)) for author in item.authors
            ]
            answer["videos"].append(temp)
        return jsonify(answer)

    @jwt_required()
    def post(self):
        session = db_session.create_session()
        current_user_id = get_jwt_identity()
        current_user = session.query(User).get(current_user_id)
        if current_user is None:
            abort(403, message="Token is wrong")
        args = parser.parse_args()
        if args.get("file", None) is None:
            abort(400, message="Missing file")
        file = args["file"]
        print(file.mimetype)
        ext = secure_filename(file.filename).rsplit(".")[-1]
        if ext not in ALLOWED_EXT:
            abort(415, message="File format isn't supported")
        authors = args["authors"].split(";")
        authors += [current_user.slug]
        video = Video(title=args["title"], description=args["description"])
        for author_slug in authors:
            author = session.query(User).filter(User.slug == author_slug).first()
            if author is not None:
                video.authors.append(author)
        short_name = video.set_short_name()
        video.ext = ext
        file.save("storage/" + short_name + "." + ext)
        session.add(video)
        session.commit()
        return jsonify({"success": "OK", "short_name": short_name})

from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, abort

from data.comments import Comment
from data.users import User
from data.videos import Video
from data import db_session

from .comment_parser import parser


def abort_if_not_found(comment_id):
    session = db_session.create_session()
    comment = session.query(Comment).get(comment_id)
    if comment is None:
        abort(404, message="Comment not founded")


class CommentListResource(Resource):
    def get(self, video_short_name):
        session = db_session.create_session()
        video = (
            session.query(Video).filter(Video.short_name == video_short_name).first()
        )
        if video is None:
            abort(404, message="Video doesn't exist")
        answer = {"comments": []}
        for item in video.comments:
            temp = item.to_dict(only=("id", "text", "created_date"))
            temp["author"] = item.author.slug
            answer["comments"].append(temp)
        return jsonify(answer)

    @jwt_required()
    def post(self, video_short_name):
        args = parser.parse_args()
        session = db_session.create_session()
        video = (
            session.query(Video).filter(Video.short_name == video_short_name).first()
        )
        if video is None:
            abort(404, message="Video doesn't exist")
        current_user_id = get_jwt_identity()
        current_user = session.query(User).get(current_user_id)
        if current_user is None:
            abort(403, message="Token is wrong")
        comment = Comment(
            text=args["text"],
            video_id=video.id,
            author_id=current_user.id,
        )
        session.add(comment)
        session.commit()
        return jsonify({"success": "OK"})


class CommentResource(Resource):
    @jwt_required()
    def delete(self, comment_id):
        abort_if_not_found(comment_id)
        session = db_session.create_session()
        current_user_id = get_jwt_identity()
        current_user = session.query(User).get(current_user_id)
        if current_user is None:
            abort(403, message="Token is wrong")
        comment = session.query(Comment).get(comment_id)
        if comment.author == current_user:
            session.delete(comment)
            session.commit()
            return jsonify({"success": "OK"})
        return jsonify({"msg": "You cannot delete not your comment"})

    def get(self, comment_id):
        abort_if_not_found(comment_id)
        session = db_session.create_session()
        comment = session.query(Comment).get(comment_id)
        answer = {"comment": comment.to_dict(only=("id", "text", "created_date"))}
        answer["comment"]["author"] = comment.author.slug
        return jsonify(answer)

    @jwt_required()
    def put(self, comment_id):
        args = parser.parse_args()
        abort_if_not_found(comment_id)
        session = db_session.create_session()
        current_user_id = get_jwt_identity()
        current_user = session.query(User).get(current_user_id)
        if current_user is None:
            abort(403, message="Token is wrong")
        comment = session.query(Comment).get(comment_id)
        if comment.author == current_user:
            comment.text = args["text"]
            session.commit()
            return jsonify({"success": "OK"})
        return jsonify({"msg": "You cannot change not your comment"})

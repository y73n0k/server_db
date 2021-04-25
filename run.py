from datetime import timedelta
from requests import get

from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    JWTManager,
)
from flask_restful import Api
from werkzeug.exceptions import default_exceptions

from init_app import app
from data import db_session
from data.users import User
from resources import user_resources, comment_resources, video_resources


api = Api(app)
api.add_resource(user_resources.UserListResource, "/users/")
api.add_resource(user_resources.UserResource, "/users/<string:slug>")
api.add_resource(
    comment_resources.CommentListResource, "/comments/<string:video_short_name>"
)
api.add_resource(comment_resources.CommentResource, "/comments/<int:comment_id>")
api.add_resource(video_resources.VideoListResource, "/videos/")
api.add_resource(video_resources.VideoResource, "/videos/<string:short_name>")

app.config["JWT_SECRET_KEY"] = "jwt-secret-string"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=2)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
app.config["PROPAGATE_EXCEPTIONS"] = True
jwt = JWTManager(app)


def handle_error(e):
    return jsonify(error=str(e), code=e.code)


for exception in default_exceptions:
    app.register_error_handler(exception, handle_error)


@app.route("/get_token")
def get_token():
    slug = request.args["slug"]
    password = request.args["password"]
    session = db_session.create_session()
    user = session.query(User).filter(User.slug == slug).first()
    if user is None:
        return jsonify({"error": 404, "message": "User doesn't exist"})
    if not user.check_password(password):
        return jsonify({"error": 403, "message": "Wrong password"})
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    return jsonify({"access_token": access_token, "refresh_token": refresh_token})


@app.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token)


@app.route("/get_me")
@jwt_required()
def get_me():
    current_user_id = get_jwt_identity()
    if current_user_id is None:
        return jsonify({"msg": "Something wrong with your token"})
    else:
        session = db_session.create_session()
        current_user = session.query(User).get(current_user_id)
        if current_user is None:
            return jsonify({"msg": "Some problems with token"})
        slug = current_user.slug
        return jsonify(get("http://127.0.0.1:4610/users/" + slug).json())


@app.before_first_request
def init_db():
    db_session.global_init("db/video_hosting.db")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=4610, debug=False)

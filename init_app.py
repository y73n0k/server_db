from flask import Flask

app = Flask(__name__, static_folder="storage")
app.config["SECRET_KEY"] = ""

from flask import Flask

app = Flask(__name__, static_folder="storage")
app.config["SECRET_KEY"] = "SUPER_DUPER_SECRET_KEY_WHICH_YOU_WILL_NEVER_GUESS_31337"

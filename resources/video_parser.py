from flask_restful import reqparse
from werkzeug.datastructures import FileStorage

parser = reqparse.RequestParser()
parser.add_argument("title", required=True)
parser.add_argument("file", required=False, type=FileStorage, location="files")
parser.add_argument("authors", required=True)
parser.add_argument("description", required=True)

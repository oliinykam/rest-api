from flask import Flask, redirect, url_for
from flask_restful import Api
from flasgger import Swagger
from app.api.api import HealthResource, BookListResource, BookResource

SWAGGER_TEMPLATE = {
    "swagger": "2.0",
    "info": {"title": "Library API", "description": "Flask + MongoDB", "version": "1.0.0"},
    "basePath": "/",
    "consumes": ["application/json"],
    "produces": ["application/json"],
    "definitions": {
        "BookRequest": {
            "type": "object",
            "required": ["title", "author", "release_year"],
            "properties": {
                "title": {"type": "string", "minLength": 1},
                "author": {"type": "string", "minLength": 1},
                "release_year": {"type": "integer", "minimum": 1},
                "status": {"type": "string", "enum": ["available", "issued"], "default": "available"},
                "description": {"type": "string", "nullable": True},
            },
        },
        "BookResponse": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "title": {"type": "string"},
                "author": {"type": "string"},
                "release_year": {"type": "integer"},
                "status": {"type": "string", "enum": ["available", "issued"]},
                "description": {"type": "string", "nullable": True},
            },
        },
    },
}

app = Flask(__name__)
swagger = Swagger(app, template=SWAGGER_TEMPLATE)
api = Api(app)

@app.route("/")
def index():
    return redirect("/apidocs/")

api.add_resource(HealthResource, "/api/health")
api.add_resource(BookListResource, "/api/books")
api.add_resource(BookResource, "/api/books/<string:book_id>")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
from flask_restful import Resource
from sytr import limiter


class HelloResource(Resource):

    @staticmethod
    @limiter.limit("1/second")
    def get():
        return {"message": "Hello, World version 1.0.0"}

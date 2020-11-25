import json
from flask import Flask
from flask_restful import Api
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_restful import Resource
from flask import jsonify, request
from sytr.translate_manager import GoogleTranslateManager
from sytr.flask_config import ProductionConfig
from sytr.utils import initlog

try:
    import uwsgi
    import uwsgidecorators
except ImportError:
    UWSGI_ENABLED = False
    uwsgi = uwsgidecorators = None
else:
    UWSGI_ENABLED = True

LOG = initlog('sytr')

LOG.info("Google Translate Backend Starting")
app = Flask(__name__)
app.config.from_object(ProductionConfig)

# add api
api = Api(app)

# Setup the app with the flask_config.py file
app.config.from_object('sytr.flask_config')

# add throttle limiter
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["10 per day", "1 per hour"]
)

gtm = GoogleTranslateManager()


class HelloResource(Resource):
    decorators = [
        limiter.limit("10/second"),
    ]

    @staticmethod
    def get():
        return {"message": "Hello, World version 1.0.0"}


class GoogleTranslateResource(Resource):
    decorators = [
        limiter.limit("10/second"),
    ]

    @staticmethod
    def post():
        # todo implement a single uwsgi mule which runs the gtm for better throttle protection

        translate_data = json.loads(request.data)
        # https://www.techatbloomberg.com/blog/configuring-uwsgi-production-deployment/
        # uwsgi locks
        if UWSGI_ENABLED:
            uwsgi.lock()
        # doing important stuff here, only process in batches of 10 at a time
        translate_result = gtm.translate_text_batch(
            text_data=translate_data["text"],
            target_language=translate_data.get("target_language", "en")
        )
        if UWSGI_ENABLED:
            uwsgi.unlock()

        return translate_result


# add resources
api.add_resource(HelloResource, '/api/health', endpoint="hello")
api.add_resource(GoogleTranslateResource, '/api/translate', endpoint="translate")
LOG.info("Google Translate Backend running")

if __name__ == "__main__":
    app.run()

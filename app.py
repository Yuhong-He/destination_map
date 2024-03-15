from flask import Flask, request
import config
from exts import db
from flask_migrate import Migrate
from services import rest_service
from utils import make_response

app = Flask(__name__)
app.config.from_object(config)

db.init_app(app)
migrate = Migrate(app, db)


@app.route('/', methods=['POST'])
def default():
    request_data = request.get_json()
    url = request_data.get('url')
    if "en.wikipedia.org" in url:
        return rest_service.handle_original_url(url)
    else:
        return make_response(404, "Can only handle English Wikipedia")


if __name__ == '__main__':
    app.run()

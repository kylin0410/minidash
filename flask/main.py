# Import build-in or 3rd-party modules
from flask import Flask, Blueprint, render_template
from flasgger import Swagger
from flask_jwt_extended import JWTManager
import logging
import sys

root = Blueprint('root', __name__)


@root.route('/', defaults={'path': ''})
@root.route('/<path:path>')
def index(path):
    return render_template('index.html')


if __name__ == '__main__':
    # Logging config.
    logging.basicConfig(
        handlers=[logging.StreamHandler(sys.stdout)],
        level=10,
        format="%(asctime)s [%(threadName)-10s] %(levelname)s " +
        "%(filename)-19s %(lineno)d\n    %(message)s\n")

    # Create main flask.
    main = Flask(__name__, template_folder='static', static_folder='static')

    # Provide swagger only in debug mode.
    Swagger(main)

    # Register blueprint.
    from api.auth import auth
    from api.dashboard import dashboard
    main.register_blueprint(root)
    main.register_blueprint(auth)
    main.register_blueprint(dashboard)
    main.debug = True
    main.config['JWT_TOKEN_LOCATION'] = ['headers'
                                         ]  # Put JWT Token in Headers.
    main.config['JWT_SECRET_KEY'] = 'this-is-your-key'  # 改成你設定的密鑰
    main.config['UPLOAD_FOLDER'] = '/tmp'
    jwt = JWTManager(main)  # JWT Token Auth

    # Start flask application.
    debug = False
    main.run(host="0.0.0.0", port=8000, debug=debug)

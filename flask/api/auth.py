# Import build-in or 3rd-party modules
import pam
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

auth = Blueprint('auth', __name__)


@auth.route('/api/auth/login', methods=['POST'])
def login():
    """
    Get access token (JWT) by login with username and password.
    ---
    tags:
      - Login API
    parameters:
      - name: body
        in: body
        required: true
        schema:
          id: login
          required:
            - name
          properties:
            username:
              type: string
              description: User name for login.
            password:
              type: string
              description: Password for login.
    responses:
      200:
        description: Authentication OK.
        schema:
          id: jwt_token
          properties:
            access_token:
              type: string
              description: Please put it in header.
      400:
        description: Bad user name or password.
      500:
        description: Fail to Authenticate.
    """
    # Validate parameters from request.
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username or not password:
        return jsonify({"msg": "Please input username and password"}), 400

    # Auth Linux system by pam module.
    p = pam.pam()
    auth = p.authenticate(username, password)

    if auth:
        ret = {
            'access_token': create_access_token(identity=username)
        }
        return jsonify(ret), 200
    return jsonify({"msg": "Invalid username or password."}), 500

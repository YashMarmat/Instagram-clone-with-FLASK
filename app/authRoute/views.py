
from datetime import timedelta
from app.postRoute.errors import bad_request, custom404, unauthorized
from . import authRoute
from flask import request, jsonify, current_app
from ..models import User, TokenBlocklist
from datetime import datetime
from datetime import timezone

from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, current_user
from flask_jwt_extended import decode_token, get_jwt
from .. import db


@authRoute.route('/login', methods=['POST'])
def login():
    email = request.json.get('email', None)
    password = request.json.get('password', None)

    user = User.query.filter_by(email=email).first()

    if not user:
        return bad_request("Email not registred.")
    
    elif not user.verify_password(password):
        return bad_request("Incorrect Password.")

    else:
        # jwt
        # config options => https://flask-jwt-extended.readthedocs.io/en/stable/options/#jwt-access-token-expires
        # more time options => https://docs.python.org/3/library/datetime.html#timedelta-objects

        wrap_data = {"user_id": user.id}

        access_token = create_access_token(
            identity=email,
            additional_claims=wrap_data,
            expires_delta=timedelta(minutes=40)
        )
        # print(decode_token(access_token))
        return jsonify(access_token=access_token, user_id=user.id)


@authRoute.route('/logout', methods=['DELETE'])
@jwt_required()
def logout():
    # token_from_client = request.json.get('access_token', None)
    # token_from_client
    jti = get_jwt()['jti']
    now = datetime.now(timezone.utc)
    db.session.add(TokenBlocklist(jti=jti, created_at=now))
    db.session.commit()

    return jsonify({ "msg" : "Logged out."})

@authRoute.route('/register', methods=['POST'])
def register():
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    username = request.json.get('username', None)

    locate_email = User.query.filter_by(email=email.lower()).first()
    locate_username = User.query.filter_by(username=username).first()

    if locate_email:
        return bad_request('Email already registered.')
    elif locate_username:
        return bad_request('Username already taken.')
    else:
        user = User(email=email.lower(), username=username, password=password)
        db.session.add(user)
        db.session.commit()

        return jsonify({"msg": "Registration Successful, Thanks."})

@authRoute.route('/update-password', methods=['POST'])
@jwt_required()
def update_passwords():

    user = User.query.get(current_user.id) # current_user in token
    old_password = request.json.get('old_password', None)
    new_password = request.json.get('new_password', None)

    if not user:
        return custom404("User not found.")
    
    elif not user.verify_password(old_password):
        return unauthorized("Incorrect old password")
    
    else:        
        user.password = new_password
        db.session.add(user)
        db.session.commit()

        return jsonify({ "msg": "Password Updated."}), 200

    
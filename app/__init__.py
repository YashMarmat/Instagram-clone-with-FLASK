
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_cors import CORS

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_name):
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    db.init_app(app)
    # jwt = JWTManager(app)
    jwt.init_app(app)

    from .postRoute import postRoute as postRouteBlueprint
    app.register_blueprint(postRouteBlueprint) 

    from .authRoute import authRoute as authRouteBlueprint
    app.register_blueprint(authRouteBlueprint)

    from .userRoute import userRoute as userRouteBlueprint
    app.register_blueprint(userRouteBlueprint)

    from .msgRoute import msgRoute as msgRouteBlueprint
    app.register_blueprint(msgRouteBlueprint)

    from .likesRoute import likesRoute as likesRouteBlueprint
    app.register_blueprint(likesRouteBlueprint)

    return app

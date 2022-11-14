import os
basedir = os.path.abspath(os.path.dirname(__file__))
from flask_jwt_extended import JWTManager


class Config:

    SECRET_KEY = "some_unique_key"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    APP_ADMIN = "xyz@gmail.com" # place your email here

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
from flask import Blueprint

likesRoute = Blueprint('likesRoute', __name__)

from . import views
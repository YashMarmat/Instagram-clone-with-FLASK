from flask import Blueprint

postRoute = Blueprint('postRoute', __name__)

from . import views, errors

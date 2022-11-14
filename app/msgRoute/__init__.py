from flask import Blueprint

msgRoute = Blueprint('msgRoute', __name__)

from . import views
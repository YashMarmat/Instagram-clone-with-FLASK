from flask import Blueprint

authRoute = Blueprint('authRoute', __name__)

from . import views
from ..postRoute import errors
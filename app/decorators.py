from app.postRoute.errors import forbidden
# from flask_jwt_extended import get_jwt_identity, current_user
# from .models import Permission, User
from flask_jwt_extended import current_user
from .models import Permission
from functools import wraps

# Note:
# a wrapper basically wraps up everthing of its function Ex: ('__module__', '__name__', '__doc__') 
# where as a simple decorator doesn't, its only meant to return the function.

def verify_user_token(func):
    @wraps(func)
    def inner_func(id):
        # logged_user_email = get_jwt_identity() # will return the email (because we set the identity=email in auth)
        # get_user_by_mail = User.query.filter_by(email=logged_user_email).first()
        # logged_user_id = get_user_by_mail.id
        
        # print("current user id:", current_user.id, id)
         
        # comparing user id present in token with the id of the user to make operations (needs to be true)
        # or the token user needs to be an Admin or Moderator to make this request
        admin_check = current_user.check_permission_exists_in_user(Permission.ADMIN)
        moderator_check = current_user.check_permission_exists_in_user(Permission.MODERATE)
        if current_user.id == id or admin_check or moderator_check:
            return func(id)
        else:
            return forbidden("Operation not allowed!")
    return inner_func


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.check_permission_exists_in_user(permission):
                return forbidden("Operation not allowed!")
            return f(*args, **kwargs)
        return decorated_function

    return decorator

def admin_required(f):
    return permission_required(Permission.ADMIN)(f)

from datetime import datetime
from datetime import timezone
from datetime import timedelta
from app.postRoute.errors import bad_request, custom404, forbidden
from ..decorators import admin_required, permission_required, verify_user_token
from . import userRoute
from flask_jwt_extended import jwt_required, get_jwt, current_user
from ..models import Permission, Post, TokenBlocklist, User
from flask import jsonify, request
from .. import db
from functools import wraps

# get user
@userRoute.route('/users/<int:id>')
@jwt_required()
# will match logged user id with the user id we are trying to fetch (needs to be equal)
@verify_user_token
def get_user(id):
    user = User.query.get(id)

    if not user:
        return custom404("User not found")
    return jsonify(user.to_json())


# update user name
@userRoute.route('/update_username', methods=['POST'])
@jwt_required()
def update_username():
    
    new_name = request.json.get('new_username')
    
    if new_name == "":
        return bad_request("username cannot be empty.")

    elif User.query.filter_by(username=new_name).first():
        return bad_request("username already taken.")

    get_user_id = current_user.id # getting from token
    

    # user_to_update = User.query.get(get_user_id)
    # user_to_update.username = new_name

    current_user.username = new_name
    db.session.add(current_user)
    db.session.commit()

    return jsonify({"msg": "username updated."}), 200


# update user email
@userRoute.route('/update_email', methods=['POST'])
@jwt_required()
def update_email():
    new_email = request.json.get('new_email')

    if new_email == "":
        return bad_request("email cannot be empty.")

    elif User.query.filter_by(email=new_email).first():
        return bad_request("email already in use.")

    current_user.email = new_email
    db.session.add(current_user)
    db.session.commit()

    return jsonify({ "msg": "email updated."})


# update user image
@userRoute.route('/update_image', methods=['POST'])
@jwt_required()
def update_user_image():
    new_image_url = request.json.get('image_url')

    if not new_image_url:
        return bad_request("image field cannot be empty.")

    current_user.user_image_url = new_image_url
    db.session.add(current_user)
    db.session.commit()

    return jsonify({"msg": "profile picture updated."})


# update password
@userRoute.route('/update_password', methods=['PUT'])
@jwt_required()
def update_user_password():
    old_pass = request.json.get('old_password', None)
    new_pass = request.json.get('new_password', None)

    if old_pass == "":
        return bad_request("old password cannot be empty.")

    elif new_pass == "":
        return bad_request("new password cannot be empty")


    elif current_user.verify_password(old_pass):
        current_user.password = new_pass
        db.session.add(current_user)
        db.session.commit()
        return jsonify({"msg": "password updated"})
    else:
        return forbidden("incorrect old password.")


# get logged user profile
@userRoute.route('/user_profile/<int:id>')
@jwt_required()
def get_user_profile(id):    

    user = User.query.get(id)

    if not user:
        return custom404("User not found")
    return jsonify(user.to_json())




# Delete User
@userRoute.route('/user/<int:id>/delete', methods=['POST'])
@jwt_required()
def delete_user(id):

    user_is_admin = current_user.check_permission_exists_in_user(Permission.ADMIN)
    user_is_moderator = current_user.check_permission_exists_in_user(Permission.MODERATE)          
    user = User.query.get(id)


    if not user:
        return custom404("User not found")
    else:
        # Note: with cascade = 'all, delete' in User model, when a user gets deleted
        # all of their posts gets deleted as well

        # if user is not an admin only then block its token
        deleted_by_admin = True
        
        if not user_is_admin or not user_is_moderator:
            old_pass = request.json.get('old_pass', None)

            if old_pass == "" or old_pass == None:
                return bad_request("password cannot be empty")

            if not user.verify_password(old_pass):
                return forbidden("incorrect password")

            deleted_by_admin = False
            # blocking the token of the user which is going to be removed
            # getting jti obj of currently logged in user token
            jti = get_jwt()['jti']
            now = datetime.now(timezone.utc)
            db.session.add(TokenBlocklist(jti=jti, created_at=now))
            db.session.commit()

        # deleting user
        db.session.delete(user)
        db.session.commit()

        custom_message = "User deleted (by admin)." if deleted_by_admin else "User deleted & token blocked."
        return jsonify({"msg": custom_message}), 204


# get all users
@userRoute.route('/users')
@jwt_required()
@admin_required
def get_users_as_admin():
    users = User.query.all()
    return jsonify({"users": [each_user.to_json() for each_user in users]}), 200


@userRoute.route('/all_users')
@jwt_required()
def get_all_users():
    users = User.query.all()
    return jsonify({"users": [each_user.less_user_info_json() for each_user in users]}), 200


# follow a user
@userRoute.route('/follow/<username>')
@jwt_required()
@permission_required(Permission.FOLLOW)
def follow_user(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        return custom404("user not found.")
    elif user.username == current_user.username:
        return bad_request("you cannot follow yourself.")    
    else:
        if current_user.is_following(user):
            return bad_request("already following the user.")
        else:
            current_user.follow(user)
            # im not using db.session.add() here, as that is already defined in the follow method of User model
            db.session.commit()
            return jsonify({"msg": f"Started Following {username}."})


# unfollow a user
@userRoute.route('/unfollow/<username>')
@jwt_required()
@permission_required(Permission.FOLLOW)
def unfollow_user(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        return custom404("user not found.")
    else:
        if not current_user.is_following(user):
            return bad_request("you are not following this user already.")
        else:
            current_user.unfollow(user)
            # im not using db.session.add() here, as that is already defined in the follow method of User model
            db.session.commit()
            return jsonify({"msg": f"Unfollowed {username}."})

# user followers
@userRoute.route('/followers/<username>')
@jwt_required()
def see_followers(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        return custom404("user not found")

    followers_data = []
    if user.username == current_user.username:
        my_followers = user.got_followed_back_list.all()
        for each_follower in my_followers:
            locate_user = User.query.get(each_follower.follower_id)
            followers_data.append(locate_user.username)
        return jsonify({"followers": followers_data})
    else:
        return forbidden("not allowed.")


# following to (returns current user following to list)
@userRoute.route('/following/<username>')
@jwt_required()
def see_following_to(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        return custom404("user not found")

    following_to_data = []
    if user.username == current_user.username:
        user_followed = user.following_to_list.all()
        for each_user in user_followed:
            locate_user = User.query.get(each_user.following_to)
            following_to_data.append(locate_user.username)
        return jsonify({"following": following_to_data})
    else:
        return forbidden("not allowed.")
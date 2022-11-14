from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from . import jwt
from flask import jsonify, current_app, abort

# scalar()
"""
Return the first element of the first result or None if no rows present. 
If multiple rows are returned, raises MultipleResultsFound.
"""

# json token index (jti), every token has this obj inside the token (can be seen by decode_token)
# token object contains (example) =>
# {'fresh': False, 'iat': 1664181055, 'jti': '03d5c78a-b888-4288-b21a-b52b29ad9e8a', 'type': 'access',
# 'sub': 'yashmarmat05@gmail.com', 'nbf': 1664181055, 'exp': 1664183455, 'user_id': 1}


class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # as jti values are 36 chars long
    jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False)

# Callback function to check if a JWT exists in the database blocklist


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()
    return token is not None


# Follow model table representation
"""
     ____________________________________
    |   follower_id   |  following_to    |
    |       1         |       2          |  user with id 1 follows user of id 2
    |       3         |       1          |  user with id 3 follows user of id 1
    |       3         |       2          |  user with id 3 also follows user of id 2
    |_________________|__________________|
"""


class Follow(db.Model):
    __tablename__ = 'follows'

    # id of a person who follows someone (A == follows ==> B)
    follower_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), primary_key=True)

    # id of the person to whom we are following to (B == got followed by ==> A)
    following_to = db.Column(
        db.Integer, db.ForeignKey('users.id'), primary_key=True)

    # time when they got followed/started following
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text())
    sent_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    sent_for = db.Column(db.Integer, db.ForeignKey('users.id'))
    shared_message = db.Column(db.Boolean, default=False)
    shared_post_path = db.Column(db.String(200))
    shared_post_of_username = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Message %r>' % self.body

    def msg_json(self):

        user_details = User.query.get(self.sent_for)        

        json_response = {
            'message_id': self.id,
            'sender': self.sent_by,
            'recipient_id': self.sent_for,
            'recipient_name': user_details.username,
            'sender_name': User.query.get(self.sent_by).username,
            'shared_status': self.shared_message,
            'shared_post_path': self.shared_post_path,
            'shared_post_of_username': self.shared_post_of_username,
            'body': self.body,
            'sent_on': self.timestamp
        }

        return json_response


class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    email = db.Column(db.String(100), unique=True, index=True)
    username = db.Column(db.String(100), unique=True, index=True)
    user_image_url = db.Column(db.Text)
    password_hash = db.Column(db.String(128))
    comments = db.relationship('Comment', backref='author_backref', lazy='dynamic')
    liked = db.relationship('PostLike', backref='user_like_backref', lazy='dynamic')

    messages_sent = db.relationship(
        'Message',
        foreign_keys=[Message.sent_by],
        backref='sender',
        lazy='dynamic'
    )

    messages_recieved = db.relationship(
        'Message',
        foreign_keys=[Message.sent_for],
        backref='receiver',
        lazy='dynamic'
    )

    # with cascade = 'all, delete' when a user gets deleted all its posts will be deleted as well
    posts = db.relationship('Post', backref='author',
                            lazy='dynamic', cascade='all, delete')

    # sending follower in the first column of table
    # keeps the record/list of users which current user is following to
    # example if user1 follows user2 and user3 we have => [<Follow 1, 2>, <Follow 1, 3>]
    following_to_list = db.relationship(
        'Follow',
        foreign_keys=[Follow.follower_id],
        backref=db.backref('follower_backref', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'  # description at end
    )

    # sending following_to in the second column of table
    # keeps the record/list of users which follows our current user
    # example if user3 follows user1 (current user) we have => [<Follow 3, 1>]
    got_followed_back_list = db.relationship(
        'Follow',
        foreign_keys=[Follow.following_to],
        backref=db.backref('following_to_backref', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'  # description at end
    )

    # checking if a current user is following a user of some id
    def is_following(self, user):
        # print("user data ===>", user) # returns the whole user
        if user.id is None:
            return False

        # if result is empty (means None) then user is not following the given user
        # checking if current follower id gets a match with
        return self.following_to_list.filter_by(following_to=user.id).first() is not None

    # follow
    def follow(self, user):
        if not self.is_following(user):
            follow_data = Follow(follower_backref=self,
                                 following_to_backref=user)
            db.session.add(follow_data)
            # to save this data we use db.session.commit() in follow view function (as after commit
            # we need to provide a return statement and that should be handled in views only)
        else:
            abort(403, "already following.")

    # unfollow
    def unfollow(self, user):
        if self.is_following(user):
            user_to_unfollow = self.following_to_list.filter_by(
                following_to=user.id).first()
            if user_to_unfollow:
                db.session.delete(user_to_unfollow)
            else:
                abort(403, "user not found")
        else:
            abort(403, "you need to follow the user first.")

    # follow back users (to find the user who follows you)
    # Note: in case of follow back we have => [<Follow 3, 1>] (the person who follows you
    # comes in first place and you comes in second place, because they are the follower and they are
    # following_to you, so we should filter_by considering follower_id)
    def got_followed_by(self, user):
        if user.id is None:
            return False
        else:
            # in current user followed_back list we are looking for a follower
            return self.got_followed_back_list.filter_by(follower_id=user.id).first() is not None

    # def followers_to_json(self):
    #     json_follower = {
    #         "username": self.username
    #     }

    #     return json_follower

    def __repr__(self) -> str:
        return '<User %r>' % self.username

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.email == current_app.config['APP_ADMIN']:
            self.role = Role.query.filter_by(name='Administrator').first()
        if self.role == None:
            self.role = Role.query.filter_by(default=True).first()

    # making password un-readable (if someone tries to read its value)
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def check_permission_exists_in_user(self, perm):  # for current user role
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.check_permission_exists_in_user(Permission.ADMIN)

    def to_json(self):

        role_name = ""
        if self.role_id is not None:
            get_role = Role.query.get(self.role_id)
            role_name = get_role.name

        followers_data = []
        following_to_data = []

        user_followers = self.got_followed_back_list.all()
        user_followed = self.following_to_list.all()

        for each_follower in user_followers:
            locate_user = User.query.get(each_follower.follower_id)
            followers_data.append({
                "user_id": locate_user.id,
                "username": locate_user.username
            })

        for each_user in user_followed:
            locate_user = User.query.get(each_user.following_to)
            following_to_data.append({
                "user_id": locate_user.id,
                "username": locate_user.username
            })

        json_user = {
            'user_id': self.id,
            'username': self.username,
            'role_id': self.role_id,
            'followers': followers_data,
            'following': following_to_data,
            'role': role_name,
            'profile_image': self.user_image_url,
            'email': self.email,
            'posts': [each_post.to_json() for each_post in self.posts]
        }

        return json_user

    def less_user_info_json(self):

        get_role = Role.query.get(self.role_id)
        role_name = get_role.name

        json_data = {
            'user_id': self.id,
            'username': self.username,
            'email': self.email,
            'role_id': self.role_id,
            'role_name': role_name,
            'profile_image': self.user_image_url, 
        }

        return json_data


# to get whole user object of logged in user (available as current_user)
@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["user_id"]
    return User.query.filter_by(id=identity).one_or_none()

# with user_lookup_error_loader if we try to fetch user data from a deleted user token
# then below handler will give a custom 404 error user not found and if we do not use the
# handler then by default it provides the email of the user which got deleted (not a valid approach)
# @jwt.user_lookup_error_loader
# def custom_user_loader_error(_jwt_header, jwt_data):
#     return jsonify({"msg": "User not found"}), 404

# you can also add the token in blocklist (this approach is used in this application)


class Post(db.Model):

    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    # title = db.Column(db.String(200), index=True)
    body = db.Column(db.Text)
    # body_html = db.Column(db.Text)
    uploaded_content_url = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='post_backref', lazy='dynamic')
    likes = db.relationship('PostLike', backref='post_like_backref', lazy='dynamic')

    def __repr__(self):
        return '<Post %r>' % self.body

    # post into json format
    def to_json(self):
        # where self contains the whole post object
        # print(self.comments.all()) # holds all the comments
        locate_user = User.query.get(self.author_id)     

        # ordered by latest comments
        json_post = {
            'id': self.id,
            'author_details': locate_user.less_user_info_json(), 
            'uploaded_content_url': self.uploaded_content_url,
            'body': self.body,
            'timestamp': self.timestamp,
            'likes': [each_like.like_json() for each_like in self.likes],
            'comments': [each_comm.comment_in_json() for each_comm in self.comments.order_by(Comment.timestamp.desc())]
        }

        return json_post

    # @staticmethod
    # def get_comments():
    #     print("recieved:", self)
    #     return True


class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer, default=0)

    def __repr__(self):
        return '<Role %r>' % self.name

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def reset_permissions(self):
        self.permissions = 0

    # Adding the roles to the database manually is time consuming and error prone, so
    # instead a class method can be added to the Role class for this purpose
    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.MODERATE],
            'Administrator': [Permission.FOLLOW, Permission.COMMENT,
                              Permission.WRITE, Permission.MODERATE,
                              Permission.ADMIN]
        }

        default_role = 'User'

        for each_role, role_permissions in roles.items():  # each_role = key, role_permissions = value
            role = Role.query.filter_by(name=each_role).first()

            if role is None:
                role = Role(name=each_role)

            # if a similar role is found then

            # if a permission already exists then adding a similar one will create duplicate permissions
            # so in order to avoid that situtation we need to reset the permissions
            # (a cleaning process basically)
            role.reset_permissions()

            for each_permission in role_permissions:
                role.add_permission(each_permission)

            role.default = (role.name == default_role)
            db.session.add(role)

        db.session.commit()


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    def comment_in_json(self):

        the_user = User.query.get(self.author_id)
        commented_by_user = the_user.less_user_info_json()

        json_response = {
            'id': self.id,
            'body': self.body,
            'timestamp': self.timestamp,
            'disabled': self.disabled,
            'commented_by': commented_by_user,
            'post_id': self.post_id
        }

        return json_response


class PostLike(db.Model):
    __tablename__ = 'postlikes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    def like_json(self):

        json_response = {
            'id': self.id,
            'liked_by': self.user_id,
            'post_liked': self.post_id,
            'liked_by_username': User.query.get(self.user_id).username
        }

        return json_response

"""
cascade='all, delete-orphan' ??

if one of the follower deletes their account then there is no need to maintain 
the followers and followed users data of that deleted user.
"""

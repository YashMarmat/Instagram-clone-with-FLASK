
from flask import jsonify, request
from flask_jwt_extended import current_user, jwt_required
from ..models import Post, PostLike
from .. import db
from . import likesRoute
from app.postRoute.errors import custom404, bad_request


@likesRoute.route('/like_unlike/<int:id>/')
@jwt_required()
def like_or_unlike(id): # id of post to like or unlike

    located_post = Post.query.get(id)

    if not located_post:
        return custom404("Post not found.")

    find_like = PostLike.query.filter_by(user_id=current_user.id, post_id=id).first()

    # if liked already then we will remove the liked entry (means unlike)
    if find_like:
        db.session.delete(find_like)
        db.session.commit()
        return jsonify({ "msg": "Post Unliked", "post_id": id, "updated_post": Post.query.get(id).to_json() }), 200


    new_like = PostLike(user_like_backref=current_user, post_like_backref=located_post)
    db.session.add(new_like)
    db.session.commit()

    return jsonify({ "msg": "Post Liked", "post_id": id, "updated_post": Post.query.get(id).to_json() }), 200
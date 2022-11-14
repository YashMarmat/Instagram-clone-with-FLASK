from flask import jsonify, request
from flask_jwt_extended import current_user, jwt_required

from app.postRoute.errors import bad_request, custom404

from ..models import Message, User
from .. import db
from . import msgRoute


@msgRoute.route('/send_message/<int:id>', methods=['POST'])
@jwt_required()
def send_message(id):
    # current_user
    receiver = User.query.get(id)
    msg_body = request.json.get('body', None)
    shared_status = request.json.get('shared_msg', None)
    shared_post_path = request.json.get('shared_post_path', None) 
    shared_post_of_username = request.json.get('shared_post_of_username', None)

    if not receiver:
        return custom404("User not found.")

    # sending message to yourself (not allowed)
    elif id == current_user.id:
        return bad_request("you cannot message yourself.")

    elif msg_body is None or msg_body == "":
        return bad_request("message cannot be empty.")

    else:
        new_msg = Message(
            body=msg_body, 
            shared_message=shared_status, 
            shared_post_path=shared_post_path,
            sender=current_user,
            receiver=receiver,
            shared_post_of_username=shared_post_of_username
        )
        db.session.add(new_msg)
        db.session.commit()
        return jsonify({"msg": "message sent."}), 200


@msgRoute.route('/sent_messages')
@jwt_required()
def sent_messages():
    user_messages = [each_msg.msg_json()
                     for each_msg in current_user.messages_sent.all()]
    return jsonify({"sent_messages": user_messages}), 200


@msgRoute.route('/received_messages')
@jwt_required()
def received_messages():
    receieved_msgs = [each_msg.msg_json()
                      for each_msg in current_user.messages_recieved.all()]
    # print("receieved_msgs =>", receieved_msgs)
    return jsonify({"received_messages": receieved_msgs})


# delete message
@msgRoute.route('/delete_message/<int:id>', methods=['DELETE'])
def delete_message(id):
    msg = Message.query.get(id)

    if not msg:
        return jsonify({"error": "message not found"}), 404

    db.session.delete(msg)
    db.session.commit()
    return jsonify({"message": "message deleted."}), 200


# id of the user with whom you chatted
@msgRoute.route('/show_conversation/<int:id>')
@jwt_required()
def show_conversation(id):
    # your_id = 3  # or current_user id, as we do not have a login system yet
    current_user_obj = current_user
    other_person = User.query.get(id)

    # consider messages_recieved like a inbox of a user, and sent_by means message sent by some
    # particular user (id in this case)
    whole_conversation = current_user_obj.messages_recieved.filter_by(sent_by=id).all() + \
        other_person.messages_recieved.filter_by(sent_by=current_user.id).all()

    # sorting conversation, use reverse=True for descending order
    # lambda method is like a shortcut to write functions in python (based on some condition)
    whole_conversation.sort(key=lambda x: x.timestamp)

    conversation_array = [each_conv.msg_json()
                          for each_conv in whole_conversation]

    return jsonify({"conversation": conversation_array})
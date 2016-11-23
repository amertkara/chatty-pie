#!/usr/bin/env python

import webapp2
from google.net.proto.ProtocolBuffer import ProtocolBufferDecodeError

from entities_validators import IllegalChatroomTypeException, IllegalChatroomStatusException
from json_helpers import json_account, get_json_value, json_accounts, json_chatroom, json_chatrooms, json_users, \
    json_posts, json_post
from services import create_account, get_all_accounts, create_chatroom, delete_chatroom, get_all_chatrooms, \
    allow_user_access_in_chatroom, \
    get_chatrooms_in, get_all_users_allowed_in, get_posts_in, create_post, \
    update_chatroom


class JsonApiHandler(webapp2.RequestHandler):
    def get_mandatory_json_value(self, key_name):
        value = get_json_value(self.request.body, key_name)
        if value is None:
            self.abort(400, "missing " + key_name + " param")
        return value

    def handle_exception(self, exception, debug_mode):
        if isinstance(exception, ProtocolBufferDecodeError):
            self.abort(400, "{ \"error\": \"invalid entity key\" }")
        elif isinstance(exception, IllegalChatroomTypeException):
            self.abort(400, "{ \"error\": \"A chatroom type must be either 'trial' or 'standard'\" }")
        elif isinstance(exception, IllegalChatroomStatusException):
            self.abort(400, "{ \"error\": \"A chatroom status must be either 'active' or 'suspended'\" }")
        else:
            self.abort(500, exception)

    def get_optional_json_value(self, key_name):
        value = get_json_value(self.request.body, key_name)
        return value


class AccountApi(JsonApiHandler):
    def get(self):
        all_accounts = get_all_accounts()
        write_json_response(self.response, 200, json_accounts(all_accounts))

    def post(self):
        max_allowed_rooms = self.get_mandatory_json_value("max_allowed_rooms")

        account = create_account(max_allowed_rooms)

        write_json_response(self.response, 201, json_account(account))


class ChatroomApi(JsonApiHandler):
    def get(self, account_id):
        all_chatrooms_in_this_account = get_chatrooms_in(account_id)
        write_json_response(self.response, 200, json_chatrooms(all_chatrooms_in_this_account))

    def get_all_rooms(self):
        all_chatrooms = get_all_chatrooms()
        write_json_response(self.response, 200, json_chatrooms(all_chatrooms))

    def post(self, account_id):
        chatroom_name = self.get_mandatory_json_value("name")
        chatroom_type = self.get_optional_json_value("type")
        chatroom_type = "standard" if chatroom_type is None else chatroom_type
        chatroom_status = self.get_optional_json_value("status")
        chatroom_status = "active" if chatroom_status is None else chatroom_status
        chatroom = create_chatroom(account_id, chatroom_name, chatroom_type, chatroom_status)
        write_json_response(self.response, 201, json_chatroom(chatroom))

    def delete(self, chatroom_id):
        delete_chatroom(chatroom_id)
        write_json_response(self.response, 200, "{\"message\": \"Delete successful\"}")

    def put(self, chatroom_id):
        chatroom_type = self.get_mandatory_json_value("type")
        chatroom_status = self.get_mandatory_json_value("status")
        update_chatroom(chatroom_id, chatroom_type, chatroom_status)
        write_json_response(self.response, 201, "{\"message\": \"Update successful\"}")


class UserAccessApi(JsonApiHandler):
    def get(self, chatroom_id):
        all_users_allowed_in_chatroom = get_all_users_allowed_in(chatroom_id)
        write_json_response(self.response, 200, json_users(all_users_allowed_in_chatroom))

    def put(self, chatroom_id):
        email = self.get_mandatory_json_value("email")
        can_see_all_history = self.get_mandatory_json_value("canSeeAllHistory")

        allow_user_access_in_chatroom(chatroom_id, email, can_see_all_history)

        self.response.status = 204


class PostApi(JsonApiHandler):
    def get(self, chatroom_id):
        all_posts_in_this_chatroom = get_posts_in(chatroom_id)
        write_json_response(self.response, 200, json_posts(all_posts_in_this_chatroom))

    def post(self, chatroom_id):
        user_email = self.get_mandatory_json_value("user_email")
        content = self.get_mandatory_json_value("content")

        post = create_post(chatroom_id, user_email, content)

        write_json_response(self.response, 201, json_post(post))


def write_json_response(response, status_code, json_body):
    response.content_type = "application/json"
    response.write(json_body)
    response.status = status_code

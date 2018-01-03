#!/usr/bin/env python

# Copyright 2017 AppDirect, Inc. and/or its affiliates
# Copyright 2016 Google Inc
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import webapp2
from google.net.proto.ProtocolBuffer import ProtocolBufferDecodeError

from json_helpers import json_account, get_json_value, json_accounts, json_chatroom, json_chatrooms, json_users, \
    json_posts, json_post, json_domain_ownership_proof
from services import create_account, get_all_accounts, create_chatroom, delete_chatroom, get_all_chatrooms, \
    allow_user_access_in_chatroom, revoke_user_access_in_chatroom,\
    get_chatrooms_in, get_all_users_allowed_in, get_posts_in, create_post, \
    update_chatroom, get_domain_ownership_proof, get_existing_ownership_proofs, get_chatroom, add_domain, delete_domain


class JsonApiHandler(webapp2.RequestHandler):
    def get_mandatory_json_value(self, key_name):
        value = get_json_value(self.request.body, key_name)
        if value is None:
            self.abort(400, "missing " + key_name + " param")
        return value

    def handle_exception(self, exception, debug_mode):
        if isinstance(exception, ProtocolBufferDecodeError):
            self.abort(400, "{ \"error\": \"invalid entity key\" }")
        elif isinstance(exception, ValueError):
            self.abort(400, "{ \"error\": \"" + exception.message + "\" }")
        elif isinstance(exception, LookupError):
            self.abort(404, "{ \"error\": \"" + exception.message + "\" }")
        elif isinstance(exception, AssertionError):
            self.abort(409, "{ \"error\": \"" + exception.message + "\" }")
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


class AccountDomainOwnershipApi(JsonApiHandler):
    def get(self, account_id, domain_name):
        domain_ownership_proof = get_domain_ownership_proof(account_id, domain_name)
        write_json_response(self.response, 200, json_domain_ownership_proof(domain_ownership_proof))


class AccountDomainApi(JsonApiHandler):
    def post(self, account_id, domain_name):
        add_domain(account_id, domain_name)
        write_json_response(self.response, 200, "")

    def delete(self, account_id, domain_name):
        delete_domain(account_id, domain_name)
        write_json_response(self.response, 200, "")


class OwnershipVerificationApi(JsonApiHandler):
    def post(self, account_id, domain_name):
        existing_ownership_proofs = get_existing_ownership_proofs(account_id, domain_name)
        if not existing_ownership_proofs:
            write_json_response(self.response, 400, """{"error" : "Cannot trigger validation, ownership proof was never requested"}""")
        else:
            write_json_response(self.response, 200, "")


class ChatroomApi(JsonApiHandler):
    def get(self, account_id):
        all_chatrooms_in_this_account = get_chatrooms_in(account_id)
        write_json_response(self.response, 200, json_chatrooms(all_chatrooms_in_this_account))

    def get_room(self, chatroom_id):
        room = get_chatroom(chatroom_id)
        write_json_response(self.response, 200, json_chatroom(room))

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

    def put(self, chatroom_id):
        chatroom_type = self.get_optional_json_value("type")
        chatroom_status = self.get_optional_json_value("status")
        chatroom_full_history_enabled = self.get_optional_json_value("full_history_enabled")
        update_chatroom(chatroom_id, chatroom_type, chatroom_status, chatroom_full_history_enabled)

        self.response.status = 204

    def delete(self, chatroom_id):
        delete_chatroom(chatroom_id)
        write_json_response(self.response, 200, "{\"message\": \"Delete successful\"}")


class AllUsersInChatroom(JsonApiHandler):
    def get(self, chatroom_id):
        all_users_allowed_in_chatroom = get_all_users_allowed_in(chatroom_id)
        write_json_response(self.response, 200, json_users(all_users_allowed_in_chatroom))


class UserAccessApi(JsonApiHandler):
    def post(self, chatroom_id, email):
        allow_user_access_in_chatroom(chatroom_id, email, False)
        self.response.status = 204

    def delete(self, chatroom_id, email):
        revoke_user_access_in_chatroom(chatroom_id, email)
        self.response.status = 204


class ChatroomPostApi(JsonApiHandler):
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

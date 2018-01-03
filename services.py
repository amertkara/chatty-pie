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

from google.appengine.ext import ndb

from entities import Account, Chatroom, Post, ChatroomUser, DomainOwnershipProof


def get_account(urlsafe_account_id):
    account = ndb.Key(urlsafe=urlsafe_account_id).get()
    if account is None or not isinstance(account, Account):
        raise LookupError("Cannot find an account with id " + urlsafe_account_id)
    return account


def get_domain_ownership_proof(urlsafe_account_id, domain_name):
    existing_ownership_proofs = get_existing_ownership_proofs(urlsafe_account_id, domain_name)
    if not existing_ownership_proofs:
        ownership_proof = DomainOwnershipProof(account_id=urlsafe_account_id, domain_name=domain_name)
        ownership_proof.put()
    else:
        ownership_proof = existing_ownership_proofs[0]

    return ownership_proof


def get_existing_ownership_proofs(urlsafe_account_id, domain_name):
    get_account(urlsafe_account_id) # load account to see if exists
    return DomainOwnershipProof \
        .query(DomainOwnershipProof.account_id == urlsafe_account_id, DomainOwnershipProof.domain_name == domain_name) \
        .fetch()


def add_domain(urlsafe_account_id, domain_name):
    existing_ownership_proofs = get_existing_ownership_proofs(urlsafe_account_id, domain_name)
    if existing_ownership_proofs:
        raise AssertionError("Domain " + domain_name + " already exists for the account with id " + urlsafe_account_id)
    else:
        new_domain = DomainOwnershipProof(account_id=urlsafe_account_id, domain_name=domain_name)
        new_domain.put()


def delete_domain(urlsafe_account_id, domain_name):
    existing_ownership_proofs = get_existing_ownership_proofs(urlsafe_account_id, domain_name)
    if not existing_ownership_proofs:
        raise LookupError("Domain " + domain_name + " does not exist for the account with id " + urlsafe_account_id)
    else:
        existing_ownership_proofs[0].key.delete()


def get_all_accounts():
    return Account.query().fetch()


def create_account(max_allowed_rooms):
    account = Account(max_allowed_rooms=max_allowed_rooms)
    account.put()

    return account


def get_all_chatrooms():
    return Chatroom.query().fetch()


def get_chatrooms_in(urlsafe_account_id):
    account = get_account(urlsafe_account_id)
    return Chatroom.query(Chatroom.account_key == account.key).fetch()


def get_chatroom(urlsafe_chatroom_id):
    chatroom = ndb.Key(urlsafe=urlsafe_chatroom_id).get()
    if chatroom is None or not isinstance(chatroom, Chatroom):
        raise LookupError("Cannot find a room with id " + urlsafe_chatroom_id)
    return chatroom


def delete_chatroom(urlsafe_chatroom_id):
    get_chatroom(urlsafe_chatroom_id).key.delete()


def create_chatroom(urlsafe_account_id, name, type, status):
    account = get_account(urlsafe_account_id)
    chatroom = Chatroom(account_key=account.key, name=name, type=type, status=status, full_history_enabled=False)
    chatroom.put()

    return chatroom


def update_chatroom(urlsafe_chatroom_id, new_type, new_status, full_history_enabled):
    chatroom = get_chatroom(urlsafe_chatroom_id)
    if new_type is not None:
        chatroom.type = new_type
    if new_status is not None:
        chatroom.status = new_status
    if full_history_enabled is not None:
        chatroom.full_history_enabled = full_history_enabled
    chatroom.put()

    return chatroom


def get_all_users_allowed_in(urlsafe_chatroom_id):
    return get_chatroom(urlsafe_chatroom_id).users_with_access


def allow_user_access_in_chatroom(urlsafe_chatroom_id, user_email, can_see_all_history):
    chatroom = get_chatroom(urlsafe_chatroom_id)
    users_with_access = chatroom.users_with_access
    existing_users = filter(lambda user: user.email == user_email, users_with_access)[:1]
    if existing_users:
        existing_users[0].can_see_all_history = can_see_all_history
    else:
        users_with_access.append(ChatroomUser(email=user_email, can_see_all_history=can_see_all_history))

    chatroom.put()


def revoke_user_access_in_chatroom(urlsafe_chatroom_id, user_email):
    chatroom = get_chatroom(urlsafe_chatroom_id)
    users_with_access = chatroom.users_with_access
    chatroom.users_with_access = filter(lambda user: user.email != user_email, users_with_access)
    chatroom.put()


def get_posts_in(urlsafe_chatroom_id):
    chatroom = get_chatroom(urlsafe_chatroom_id)
    return Post.query(Post.chatroom_key == chatroom.key).fetch()


def create_post(urlsafe_chatroom_id, user_email, content):
    chatroom = get_chatroom(urlsafe_chatroom_id)
    if chatroom.status != 'active':
        raise ValueError("Posts cannot be published while chatroom is suspended.")
    post = Post(chatroom_key=chatroom.key, user_email=user_email, content=content)
    post.put()

    return post

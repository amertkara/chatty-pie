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

from api_handlers import AccountApi, ChatroomApi, UserAccessApi, AllUsersInChatroom, ChatroomPostApi, AccountDomainOwnershipApi, \
    OwnershipVerificationApi, AccountDomainApi
from error_handlers import handle_400, handle_404, handle_409, handle_500
from html_handlers import RedirectToAccounts, AllAccounts, SingleAccount, SingleRoom, AllRooms

app = webapp2.WSGIApplication([
    webapp2.Route('/', RedirectToAccounts),
    webapp2.Route('/accounts', AccountApi),
    webapp2.Route('/accounts/list', AllAccounts),
    webapp2.Route('/accounts/view', SingleAccount),
    webapp2.Route('/accounts/<account_id>/domains/<domain_name>', AccountDomainApi),
    webapp2.Route('/accounts/<account_id>/domains/<domain_name>/ownershipProof', AccountDomainOwnershipApi),
    webapp2.Route('/accounts/<account_id>/domains/<domain_name>/triggerOwnershipVerification', OwnershipVerificationApi),
    webapp2.Route('/accounts/<account_id>/rooms', ChatroomApi),
    webapp2.Route('/rooms', ChatroomApi, methods=["GET"], handler_method="get_all_rooms"),
    webapp2.Route('/rooms/view', SingleRoom),
    webapp2.Route('/rooms/list', AllRooms),
    webapp2.Route('/rooms/<chatroom_id>/users', AllUsersInChatroom),
    webapp2.Route('/rooms/<chatroom_id>/users/<email>', UserAccessApi),
    webapp2.Route('/rooms/<chatroom_id>/posts', ChatroomPostApi),
    webapp2.Route('/rooms/<chatroom_id>', ChatroomApi, methods=["GET"], handler_method="get_room")
], debug=True)
app.error_handlers[400] = handle_400
app.error_handlers[404] = handle_404
app.error_handlers[409] = handle_409
app.error_handlers[500] = handle_500

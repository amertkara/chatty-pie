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


def handle_400(request, response, exception):
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    response.write(exception)
    response.set_status(400)
    return


def handle_404(request, response, exception):
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    response.write(exception)
    response.set_status(404)
    return


def handle_409(request, response, exception):
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    response.write(exception)
    response.set_status(409)
    return


def handle_500(request, response, exception):
    response.write(exception)
    response.set_status(500)
    return

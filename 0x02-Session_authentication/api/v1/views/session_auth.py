#!/usr/bin/env python3
'''Implement a view for login
'''
import os
from api.v1.views import app_views
from models.user import User
from flask import request, session, make_response, jsonify


@app_views.route('auth_session/login', methods=['POST'], strict_slashes=False)
def login():
    '''Log a user in using session authentication
    '''
    user_email = request.form.get('email')
    user_password = request.form.get('password')

    if user_email is None or user_email == '':
        return {"error": "email missing"}, 400
    if user_password is None or user_password == '':
        return {"error": "password missing"}, 400

    user = User.search({'email': user_email})
    user = None if user == [] else user[0]
    if user is None:
        return {"error": "no user found for this email"}, 404
    elif not user.is_valid_password(user_password):
        return {"error": "wrong password"}, 401
    else:
        from api.v1.app import auth
        session_id = auth.create_session(user.id)
        resp = make_response(jsonify(user.to_json()))
        cookie_name = os.getenv('SESSION_NAME')
        resp.set_cookie(cookie_name, session_id)
        return resp

@app_views.route(
    'auth_session/logout', methods=['DELETE'], strict_slashes=False)
def logout():
    '''Delete session cookies and log a user out
    '''
    from api.v1.app import auth

    destroyed = auth.destroy_session(request)
    if destroyed is False:
        abort(404)
    else:
        return jsonify({}), 200
    

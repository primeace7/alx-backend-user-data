#!/usr/bin/env python3
'''Flask app to provide authenticated API service
'''
from flask import Flask, jsonify, request, abort,\
    make_response, url_for, redirect
from auth import Auth


app = Flask(__name__)
AUTH = Auth()


@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Bienvenue"})


@app.route('/users', methods=['POST'], strict_slashes=False)
def users():
    '''Register a new user and store in the database'''
    email = request.form.get('email')
    password = request.form.get('password')

    try:
        AUTH.register_user(email=email, password=password)
        return jsonify({"email": email, "message": "user created"})
    except ValueError:
        return jsonify({"message": "email already registered"}), 400


@app.route('/sessions', methods=['POST'], strict_slashes=False)
def login():
    '''Log a user in and assign them a session'''
    email = request.form.get('email')
    password = request.form.get('password')
    if email is None or password is None:
        abort(401)

    if not AUTH.valid_login(email, password):
        abort(401)

    session_id = AUTH.create_session(email)
    response = make_response(jsonify(
        {"email": email, "message": "logged in"}))
    response.set_cookie('session_id', session_id)
    return response


@app.route('/sessions', methods=['DELETE'], strict_slashes=False)
def logout():
    '''Log a user out, delete their session and redirect to home
    '''
    session_id = request.cookies.get('session_id')
    if session_id is None:
        abort(403)

    user = AUTH.get_user_from_session_id(session_id)
    if user is None:
        abort(403)

    AUTH.destroy_session(user.id)
    return redirect(url_for('home'))


@app.route('/profile', methods=['GET'], strict_slashes=False)
def profile():
    '''Get a user from their session id and return their email
    '''
    session_id = request.cookies.get('session_id')
    if session_id is None:
        abort(403)

    user = AUTH.get_user_from_session_id(session_id)
    if user is None:
        abort(403)

    return jsonify({"email": user.email})


@app.route('/reset_password', methods=['POST'], strict_slashes=False)
def get_reset_password_token():
    '''Generate a password reset token for a user
    '''
    email = request.form.get('email')
    if email is None:
        abort(403)
    try:
        reset_token = AUTH.get_reset_password_token(email)
        return jsonify({"email": email, "reset_token": reset_token})
    except ValueError:
        abort(403)


@app.route('/reset_password', methods=['PUT'], strict_slashes=False)
def update_password():
    '''Update a user's password'''
    email = request.form.get('email')
    reset_token = request.form.get('reset_token')
    new_password = request.form.get('new_password')

    try:
        AUTH.update_password(reset_token, password)
        return jsonify({"email": email, "message": "Password updated"})

    except ValueError:
        abort(403)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")

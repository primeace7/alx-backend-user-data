#!/usr/bin/env python3
"""
Integration tests for user authentication service
"""
import requests
import json


def register_user(email: str, password: str) -> None:
    '''test user registration'''

    response = requests.post(
        '0.0.0.0:5000/users', data={'email': email, 'password': password})

    assert response.status_code == 200
    assert response.json() == {"email": email, "message": "user created"}

    response2 = requests.post(
        '0.0.0.0:5000/users', data={'email': email, 'password': password})

    assert response2.status_code == 400
    assert response2.json() == {"message": "email already registered"}


def log_in_wrong_password(email: str, password: str) -> None:
    '''Test user login with wrong password'''

    response = requests.post(
        '0.0.0.0:5000/sessions', data={'email': email, 'password': password})

    assert response.status_code == 401


def log_in(email: str, password: str) -> str:
    '''Test user login with correct credentials'''

    response = requests.post(
        '0.0.0.0:5000/sessions', data={'email': email, 'password': password})

    assert response.status_code == 200
    assert response.json() == {"email": email, "message": "logged in"}

    assert 'session_id' in response.cookies.keys()
    return response.text


def profile_unlogged() -> None:
    '''Test a user's profile view, but without required cookie'''

    response = requests.get('0.0.0.0:5000/profile')
    assert response.status_code == 403


def profile_logged(session_id: str) -> None:
    '''Test a user's profile view with correct credentials'''

    cookie = {'session_id': session_id}
    response = requests.get('0.0.0.0:5000/profile', cookies=cookie)

    assert response.status_code == 200
    assert 'email' in response.json().keys()
    assert len(response.json().keys()) == 1


def log_out(session_id: str) -> None:
    '''Test user logout feature'''

    cookie = {'session_id': session_id}
    response = requests.delete('0.0.0.0:5000/sessions', cookies=cookie)

    assert int(response.status_code) // 100 == 3


def reset_password_token(email: str) -> str:
    '''Test user reset password feature'''

    response = requests.post(
        '0.0.0.0:5000/reset_password', data={'email': email})

    response_json = response.json()
    assert 'email' in response_json.keys()
    assert 'reset_token' in response_json.keys()
    assert len(response_json.keys()) == 2
    assert response.status_code == 200

    return response.text


def update_password(email: str, reset_token: str, new_password: str) -> None:
    '''Test user update password feature'''

    payload = {'email': email, 'reset_token': reset_token,
               'new_password': new_password}
    response = requests.post('0.0.0.0:5000/reset_password', data=payload)

    assert response.status_code == 200
    assert response.json() == {"email": email, "message": "Password updated"}


EMAIL = "guillaume@holberton.io"
PASSWD = "b4l0u"
NEW_PASSWD = "t4rt1fl3tt3"


if __name__ == "__main__":

    register_user(EMAIL, PASSWD)
    log_in_wrong_password(EMAIL, NEW_PASSWD)
    profile_unlogged()
    session_id = log_in(EMAIL, PASSWD)
    profile_logged(session_id)
    log_out(session_id)
    reset_token = reset_password_token(EMAIL)
    update_password(EMAIL, reset_token, NEW_PASSWD)
    log_in(EMAIL, NEW_PASSWD)

#!/usr/bin/env python3
'''User authenticator service implementation
'''
import bcrypt
from db import DB
from uuid import uuid4
from typing import Union
from user import User
from sqlalchemy.orm.exc import NoResultFound


def _hash_password(password: str) -> str:
    '''Hash a password with bcrypt and return
    the hash
    '''
    pwd = password.encode()
    return bcrypt.hashpw(pwd, bcrypt.gensalt())


def _generate_uuid() -> str:
    '''Generate a uuid4 object and return it as
    a string
    '''
    return str(uuid4())


class Auth:
    """Auth class to interact with the authentication database.
    """

    def __init__(self):
        self._db = DB()

    def register_user(self, email: str, password: str) -> User:
        '''Register a new user, store in the
        database and return the user object'''
        try:
            user = self._db.find_user_by(email=email)
            raise ValueError(f'User {email} already exists')
        except NoResultFound:
            pwd = _hash_password(password)
            user = self._db.add_user(email=email, hashed_password=pwd)
            return user

    def valid_login(self, email: str, password: str) -> bool:
        '''Determine if a user's login credentials
        are valid
        '''
        try:
            user = self._db.find_user_by(email=email)
            if bcrypt.checkpw(password.encode(), user.hashed_password):
                return True
            return False
        except NoResultFound:
            return False

    def create_session(self, email: str) -> Union[str, None]:
        '''Create a new user session and return the session id
        '''
        try:
            user = self._db.find_user_by(email=email)
            session_id = _generate_uuid()
            self._db.update_user(user.id, session_id=session_id)
            return session_id

        except NoResultFound:
            return None

    def get_user_from_session_id(self, session_id: str) -> Union[User, None]:
        '''Given a session id, find the corresponding
        user object and return it
        '''
        if session_id is None:
            return None
        try:
            user = self._db.find_user_by(session_id=session_id)
            return user

        except NoResultFound:
            return None

    def destroy_session(self, user_id: str) -> None:
        '''Given a user_id, destroy the associated user's session
        '''
        try:
            user = self._db.find_user_by(user_id=int(user_id))
            self._db.update_user(user.id, session_id=None)
            return None

        except NoResultFound:
            return None

    def get_reset_password_token(self, email: str) -> None:
        '''Generate a token for user to reset password'''
        try:
            user = self._db.find_user_by(email=email)
            reset_token = uuid4()
            self._db.update_user(user.id, reset_token=reset_token)

        except NoResultFound:
            raise ValueError

    def update_password(self, reset_token: str, password: str) -> None:
        '''Update a user's password using their reset_password token'''
        try:
            user = self._db.find_user_by(reset_token=reset_token)
            hashed_password = _hash_password(password)
            self._db.update_user(
                user.id, hashed_password=hashed_password,
                reset_token=None)
            return None

        except NoResultFound:
            raise ValueError

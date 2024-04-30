#!/usr/bin/env python3
''' Implement a basic authenticator from Auth base class'''
from api.v1.auth.auth import Auth
from models.user import User
from typing import TypeVar
import base64
import binascii


class BasicAuth(Auth):
    ''' Basic authentication implementation'''

    def extract_base64_authorization_header(
            self, authorization_header: str) -> str:
        ''' Extract the authentication value from authentication header'''
        if not isinstance(authorization_header, str):
            return None
        elif authorization_header is None:
            return None
        elif authorization_header[:6] != 'Basic ':
            return None
        return authorization_header[6:]

    def decode_base64_authorization_header(
            self, base64_authorization_header: str) -> str:
        ''' Decode the authentication value in base64'''
        if base64_authorization_header is None:
            return None
        elif not isinstance(base64_authorization_header, (str, bytes)):
            return None

        try:
            result = base64.b64decode(base64_authorization_header).decode()
        except (binascii.Error, UnicodeDecodeError):
            return None

        return result

    def extract_user_credentials(
            self, decoded_base64_authorization_header: str) -> (str, str):
        ''' Extract user info from authentication header value '''
        if decoded_base64_authorization_header is None:
            return None, None
        elif not isinstance(decoded_base64_authorization_header, str):
            return None, None
        elif ':' not in decoded_base64_authorization_header:
            return None, None
        result = tuple(decoded_base64_authorization_header.split(':', 1))
        return result

    def user_object_from_credentials(
            self, user_email: str, user_pwd: str) -> TypeVar('User'):
        ''' Retrieve user object from database using provided
        authentication values
        '''
        if user_email is None or not isinstance(user_email, str):
            return None
        elif user_pwd is None or not isinstance(user_pwd, str):
            return None

        if User.count() == 0:
            return None
        users = User.search({'email': user_email})
        if len(users) == 0:
            return None

        result = []
        for user in users:
            if user.is_valid_password(user_pwd):
                result.append(user)
        return result

    def current_user(self, request=None) -> TypeVar('User'):
        ''' Retrieve current user for a request from storage'''
        auth_header = self.authorization_header(request)
        auth_64 = self.extract_base64_authorization_header(auth_header)
        auth_raw = self.decode_base64_authorization_header(auth_64)
        user_login = self.extract_user_credentials(auth_raw)
        user = self.user_object_from_credentials(user_login[0], user_login[1])
        return user

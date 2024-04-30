#!/usr/bin/env python3
'''Basic authentication implementer class'''
from flask import request
from typing import (List, TypeVar)
import re


class Auth:
    '''
    Basic authentication base class
    '''
    def require_auth(self, path: str, excluded_paths: List[str]) -> bool:
        ''' Determine if an endpoint requires authentication'''
        if path and path[-1] != '/':
            path += '/'

        if excluded_paths is None or len(excluded_paths) == 0:
            return True
        elif path is None:
            return True
        for item in excluded_paths:
            if re.match(item, path):
                return False
        return True

    def authorization_header(self, request=None) -> str:
        ''' Fetch the Authorization header content'''
        if request is None:
            return None
        elif 'Authorization' not in request.headers:
            return None

        return request.headers['Authorization']

    def current_user(self, request=None) -> TypeVar('User'):
        '''Return current user'''
        return None

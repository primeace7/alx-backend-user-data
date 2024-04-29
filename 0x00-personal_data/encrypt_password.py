#!/usr/bin/env python3
'''Generate a password hash with bcrupt before storing'''
import bcrypt


def hash_password(password: str) -> bytes:
    '''Generate a password hash with bcrypt'''
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def is_valid(hashed_password: bytes, password: str) -> bool:
    '''Check an input password against the hashed version'''
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

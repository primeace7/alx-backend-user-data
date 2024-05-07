#!/usr/bin/env python3
'''Define a user model'''

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String


Base = declarative_base()

class User(Base):
    '''Define user object db structure'''
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    hashed_password = Column(String, nullable=True)
    session_id = Column(String, nullable=True)
    reset_token = Column(String, nullable=True)

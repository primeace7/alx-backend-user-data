#!/usr/bin/env python3
"""DB module
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import InvalidRequestError, NoResultFound
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from typing import Mapping, Union
from user import User

from user import Base, User


class DB:
    """DB class
    """

    def __init__(self) -> None:
        """Initialize a new DB instance
        """
        self._engine = create_engine("sqlite:///a.db", echo=False)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """Memoized session object
        """
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        '''Create a new user and save to the database'''
        new_user = User(email=email, hashed_password=hashed_password)
        self._session.add(new_user)
        self._session.commit()
        return new_user

    def find_user_by(self, **kwargs) -> User:
        '''Search for and return a row from db filtered by *kwargs'''
        for arg in kwargs.keys():
            if arg not in User.__table__.columns:
                raise InvalidRequestError

        result = self._session.query(User).filter_by(**kwargs).first()

        if not result:
            raise NoResultFound

        return result

    def update_user(self, user_id: int, **kwargs) -> None:
        '''update a user in the database'''
        user = self.find_user_by(id=user_id)

        for key, val in kwargs.items():
            if key not in User.__table__.columns:
                raise ValueError
            setattr(user, key, val)
        self._session.add(user)
        self._session.commit()

#!/usr/bin/env python3
'''Obfuscate personal data in log data'''
import re
from typing import List
import logging
from mysql.connector import connection
import os

PII_FIELDS = ('name', 'email', 'phone', 'ssn', 'password')


def filter_datum(fields: List[str], redaction: str, message: str,
                 separator: str) -> str:
    '''find and replace sensitive fields in log data with regex'''
    for field in fields:
        message = re.sub(r'({})=.*?{}'.format(field, separator),
                         r'\1={}{}'.format(redaction, separator), message)
    return message


class RedactingFormatter(logging.Formatter):
    """ Redacting Formatter class
        """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        '''return a formated log message'''
        record.msg = filter_datum(self.fields,
                                  self.REDACTION, record.msg, self.SEPARATOR)
        return super().format(record)


def get_logger() -> logging.Logger:
    '''Create and return a Logger object'''
    user_data = logging.Logger('user_data')
    user_data.propagate = False
    user_data.setLevel(logging.INFO)
    handle = logging.StreamHandler()
    handle.setFormatter(RedactingFormatter(PII_FIELDS))
    user_data.addHandler(handle)
    return user_data


def get_db() -> connection.MySQLConnection:
    '''Create and return a mysql db connector'''
    data = {
        'user': os.getenv('PERSONAL_DATA_DB_USERNAME', default='root'),
        'password': os.getenv('PERSONAL_DATA_DB_PASSWORD', default=''),
        'host': os.getenv('PERSONAL_DATA_DB_HOST', default='localhost'),
        'database': os.getenv('PERSONAL_DATA_DB_NAME')
        }

    conx = connection.MySQLConnection(**data)
    return conx


def main() -> None:
    '''Fetch data from mysql db and redact PII bfore displaying'''
    conx = get_db()
    cursor = conx.cursor(dictionary=True)
    query = 'SELECT * FROM users;'

    cursor.execute(query)
    logger = get_logger()

    for data in cursor:
        line_data = [col_name + '=' + str(item) for
                     col_name, item in data.items()]
        line = ';'.join(line_data)
        logger.info(line)

    conx.close()


if __name__ == '__main__':
    main()

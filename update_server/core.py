import logging

import peewee_async

import settings
from emailManager import EmailManager

_db = peewee_async.MySQLDatabase(database=settings.DB_NAME,
                                 host=settings.DB_HOST, port=settings.DB_PORT,
                                 user=settings.DB_USER, password=settings.DB_PASSWORD,
                                 charset=settings.DB_CHARSET)
_db.set_allow_sync(settings.ALLOW_SYNC)
_objects = peewee_async.Manager(_db)

_logger = logging.getLogger(settings.LOG_NAME)
_logger.setLevel(getattr(logging, settings.LOG_LEVEL))
_sHandle = logging.StreamHandler()
_sHandle.setLevel(getattr(logging, settings.LOG_LEVEL))
_sHandle.setFormatter(logging.Formatter(settings.LOG_FORMATTER))
_logger.addHandler(_sHandle)
if settings.LOG_FILE:
    fHandle = logging.FileHandler(settings.LOG_FILE)
    fHandle.setLevel(getattr(logging, settings.LOG_LEVEL))
    fHandle.setFormatter(logging.Formatter(settings.LOG_FORMATTER))
    _logger.addHandler(fHandle)

_emailManager = EmailManager(host=settings.EMAIL_HOST,
                             port=settings.EMAIL_PORT,
                             user=settings.EMAIL_HOST_USER,
                             password=settings.EMAIL_HOST_PASSWORD,
                             charset=settings.EMAIL_CHARSET)


def get_database():
    return _db


def get_database_manager():
    return _objects


def get_logger():
    return _logger


def get_email_manager():
    return _emailManager

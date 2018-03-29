# -*- coding: utf-8 -*-
DEBUG = False
TESTING = True
SQLALCHEMY_TRACK_MODIFICATIONS = True
SECRET_KEY = 'lol'

WTF_CSRF_CHECK_DEFAULT = False

LOGIN_DISABLED = True
SECURITY_REGISTERABLE = True
SECURITY_CONFIRMABLE = False
SECURITY_RECOVERABLE = True
SECURITY_CHANGEABLE = True
SECURITY_SEND_REGISTER_EMAIL = False
SECURITY_SEND_PASSWORD_CHANGE_EMAIL = False

SEARCH_PAGINATION_PER_PAGE = 50
MAX_ENTITIES_PER_CORPUS_PAGE = 100
SUGGESTIONS_PER_QUERY = 100

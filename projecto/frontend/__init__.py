# -*- coding: utf-8 -*-
from flask import Blueprint

frontend_bp = Blueprint('frontend', __name__, template_folder='templates')
api_bp = Blueprint(
    'api',
    __name__,
    template_folder='templates',
    url_prefix='/api')

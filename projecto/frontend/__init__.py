# -*- coding: utf-8 -*-
from flask import Blueprint

frontend_bp = Blueprint('frontend', __name__, template_folder='templates')

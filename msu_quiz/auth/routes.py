import functools
from loguru import logger
from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from loguru import logger


auth_bp = Blueprint(
    'auth', __name__,
    template_folder='templates',
    static_folder='static'
)

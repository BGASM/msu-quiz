import functools
from loguru import logger
from msu_quiz.models.models import Question, Quiz, User
from msu_quiz import db, login_manager
from flask import Blueprint, redirect, render_template, session, request, url_for, flash
from flask_login import login_required, logout_user, current_user, login_user
from msu_quiz.utils.forms import SignupForm, LoginForm
import datetime


from loguru import logger


auth_bp = Blueprint(
    'auth', __name__,
    template_folder='templates',
    static_folder='static'
)


@auth_bp.route("/register", methods=("GET", "POST"))
def register():
    """Register a new user.

    Validates that the username is not already taken. Hashes the
    password for security.
    """
    form = SignupForm()

    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user is None:
            user = User(email=form.email.data,
                        name=form.name.data,
                        username=form.username.data,
                        active=True)
            user.passwd = form.password.data
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('quiz.index'))
    return render_template('user/register.html', form=form)


@auth_bp.route("/login", methods=("GET", "POST"))
def login():
    """Log in a registered user by adding the user id to the session."""
    logger.critical('In login.')
    if current_user.is_authenticated:
        return redirect(url_for('quiz.index'))
    form = LoginForm()
    # Validate login attempt
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(password=form.password.data):
            login_user(user)
            user.update_last_on()
            next_page = request.args.get('next')
            flash('You have successfully logged in!')
            return redirect(next_page or url_for('quiz.index'))
        flash('Invalid username/password combination')
        return redirect(url_for('auth.login'))
    logger.critical('About to return.')
    return render_template("user/login.html", form=form)


@login_manager.user_loader
def load_user(user_id):
    """Check if user is logged-in on every page load."""
    return User.query.get(user_id)


@auth_bp.route("/logout", methods=("GET", "POST"))
def logout():
    logout_user()
    return redirect(url_for("quiz.index"))

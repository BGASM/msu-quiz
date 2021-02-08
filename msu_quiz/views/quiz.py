from msu_quiz.models.models import Quiz, User, QuizSchema
from msu_quiz import db
from . import domain as dom
from flask_login import login_required, current_user
from flask import Blueprint, redirect, render_template, request, url_for, jsonify
from msu_quiz.utils.mail import send_mail
from msu_quiz.utils.security import ts
from msu_quiz.utils.forms import AddQuestionForm, EmailForm, PasswordForm
from loguru import logger

myExam = dom.MyExam()


quiz_bp = Blueprint(
    'quiz', __name__,
    template_folder='templates',
    static_folder='static'
)

api_bp = Blueprint('api', __name__)


@quiz_bp.route('/reset/<token>', methods=["GET", "POST"])
def reset_with_token(token):
    try:
        email = ts.loads(token, salt="recover-key", max_age=86400)
    except:
        abort(404)

    form = PasswordForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=email).first_or_404()

        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('auth.login'))

    return render_template('user/reset_with_token.html', form=form, token=token)


@quiz_bp.route('/reset', methods=["GET", "POST"])
def reset():
    form = EmailForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first_or_404()

        subject = "Password reset requested"

        # Here we use the URLSafeTimedSerializer we created in `util` at the
        # beginning of the chapter
        token = ts.dumps(user.email, salt='recover-key')

        recover_url = url_for(
            'quiz.reset_with_token',
            token=token,
            _external=True)

        html = render_template(
            'email/recover.html',
            recover_url=recover_url)

        # Let's assume that send_email was defined in myapp/util.py
        send_mail(user.email, subject, html)

        return redirect(url_for('quiz.index'))
    return render_template('user/reset.html', form=form)


@quiz_bp.route('/check', methods=['GET', 'POST'])
@login_required
def check():
    return render_template('pages/check.html')

@quiz_bp.route('/hiv', methods=['GET', 'POST'])
def hiv():
    return render_template('pages/hiv.html')


@quiz_bp.route('/', methods=['GET', 'POST'])
def index():
    return render_template('pages/index.html')


@api_bp.route("/get_exam")
@login_required
def get_exam():
    return {'exam_data': myExam.dump}


@quiz_bp.route('/exam', methods=['GET', 'POST'])
@login_required
def exam():
    logger.debug('In Exam Function.')
    if request.method == "POST":
        return myExam.score_exam(request.get_json())
    return render_template('pages/exam.html')


@quiz_bp.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
    schema = QuizSchema(only=("id", "title", "course", "no_questions", "user", "ranking"))
    if request.method == "POST":
        return myExam.create_exam(quiz_id_list=request.get_json(), user=current_user)
    return render_template('pages/quiz.html', rows=schema.dump(Quiz.query.all(), many=True))


@quiz_bp.route('/add_question', methods=['GET', 'POST'])
@login_required
def add_question():
    form = AddQuestionForm()
    if request.method == 'POST':
        return dom.add_quiz(form=form, user=current_user.name)
    return render_template('pages/add_question.html', form=form)


# <-------------------DB stuff--------------------->








from msu_quiz.models.models import MCQ, Question, Quiz, User
from sortedcontainers.sorteddict import SortedDict
from msu_quiz import db
from flask_login import login_required, current_user
from flask import Blueprint, redirect, render_template, session, flash, request, url_for
from msu_quiz.utils.mail import send_mail
from msu_quiz.utils.security import ts
from msu_quiz.utils.add_quiz import add_quiz
from msu_quiz.utils.forms import AddQuestionForm, EmailForm, PasswordForm
from collections import namedtuple
import re
from loguru import logger
import random as rand
from pprint import pprint
import json


quiz_bp = Blueprint(
    'quiz', __name__,
    template_folder='templates',
    static_folder='static'
)


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
    qlist = []

    for item in session['question_index']:
        logger.critical(item)
        mcqs = []
        tempR = None
        for mc in item['mcq_order']:
            mcqs.append({'id': mc, 'mc': db.session.query(MCQ.mcq).filter(MCQ.id == mc).first()[0]})
        tempR = {
            'test_no': item['test_no'],
            'choice': int(item['choice']),
            'answer': item['answer'],
            'correct': item['correct'],
            'question': db.session.query(Question.question).filter(Question.id == item['question']).first()[0],
            'mcq': mcqs
        }
        qlist.append(tempR)

    for n in qlist:
        print(n)
    return render_template('pages/check.html', qlist=qlist)

@quiz_bp.route('/question_return')
def question_return():
    test_no = request.args.get("test_no")
    ind = int(test_no) - 1
    mcqs = []
    index = session['question_index'][ind]
    question = db.session.query(Question.question).filter(Question.id == index['QA']['question']).first()[0]
    for mc in index['QA']['mcqs']:
        mcqs.append([mc, db.session.query(MCQ.mcq).filter(MCQ.id == mc).first()[0]])
    return render_template('pages/question_return.html', question=question, mcqs=mcqs, test_no=test_no)


@quiz_bp.route('/', methods=['GET', 'POST'])
def index():
    return render_template('pages/index.html')


@quiz_bp.route('/exam', methods=['GET', 'POST'])
@login_required
def exam():
    if request.method == "POST":
        selected = request.get_json()
        logger.debug(selected)
        check_exam(selected)
        return url_for('quiz.check')
    logger.debug(session['question_index'])
    return render_template('pages/exam.html', qlist=session['question_index'])


@quiz_bp.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
    rows = Quiz.query.all()
    selected = []
    if request.method == "POST":
        selected = request.get_json()
        make_exam(selected)
        return url_for('quiz.exam')
    logger.debug(f"\n{rows}")
    return render_template('pages/quiz.html', rows=rows)


@quiz_bp.route('/add_question', methods=['GET', 'POST'])
@login_required
def add_question():
    form = AddQuestionForm()
    if request.method == 'POST':
        return add_quiz(form=form, user=current_user.name)
    return render_template('pages/add_question.html', form=form)


# <-------------------DB stuff--------------------->
def check_exam(sel):
    selected = SortedDict(sel)
    returned = []
    logger.debug(selected)
    for item in selected:
        temp = db.session.query(MCQ).filter_by(id=selected[item]).first()
        returned.append({'test_no': item,
                         'question': session['question_index'][int(item)-1]['QA']['question'],
                         'answer': temp.get_answer(),
                         'mcq_order': session['question_index'][int(item)-1]['QA']['mcqs'],
                         'choice': selected[item],
                         'correct': temp.check_answer()})
    sort_list = sorted(returned, key=lambda i: (int(i['test_no'])))
    session['question_index'] = sort_list
    logger.critical(session['question_index'])


def make_exam(quiz_id_list):
    question_index = []
    exam_list = []
    for quiz_id in quiz_id_list:
        for question in db.session.query(Question).filter_by(quiz_id=quiz_id[5]).all():
            mcq_id = [mcq.id for mcq in question.mcqs]
            rand.shuffle(mcq_id)
            tempq = {'question': question.id, 'mcqs': mcq_id}
            question_index.append(tempq)
    rand.shuffle(question_index)
    logger.debug(question_index)
    for index, value in enumerate(question_index, start=1):
        exam_list.append({'test_no': index, 'QA': value})
    logger.debug(exam_list)
    session['question_index'] = exam_list


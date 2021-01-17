from ..models import MCQ, Question, Quiz, User, db
from flask import Blueprint
from flask import current_app as app
from flask import session
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
import os
from loguru import logger
import random as rand

quiz_bp = Blueprint(
    'quiz', __name__,
    template_folder='templates',
    static_folder='static'
)

@quiz_bp.route('/question_return')
def question_return():
    question = request.args.get("question")
    q_id = request.args.get("id")
    t_no = request.args.get("t_no")
    body = session['body'][int(t_no)-1]
    return render_template('quiz/question_return.html', question_body=body[0], answer=body[1], mcq=body[2], test_no=t_no)


@quiz_bp.route('/', methods=['GET', 'POST'])
def index():
    user = ''
    if g.user:
        user = g.user['name']
    if request.method == 'POST':
        if "practice" in request.form:
            return redirect(url_for('quiz_bp.quiz'))
        elif "add" in request.form:
            return redirect(url_for('quiz_bp.add_question'))
    logger.debug(user)
    return render_template('index.html', user=user)


@quiz_bp.route('/exam', methods=['GET', 'POST'])
def exam():
    if 'exam' in session:
        return render_template('exam.html', qlist=session['exam'])


@quiz_bp.route('/quiz', methods=['GET', 'POST'])
def quiz():
    rows = list_quizzes()
    requested = []
    body = []
    if request.method == "POST":
        selected = request.get_json()
        for qz in selected:
            requested.extend(get_qID(qz[5]))
        rand.shuffle(requested)
        for count, value in enumerate(requested, start=1):
            value.insert(0, count)
        session['exam'] = requested
        for req in requested:
            body.append(get_question(req[2], req[1]))
        session['body'] = body
        return redirect(url_for('quiz_bp.exam'))
    logger.debug(rows)
    return render_template('quiz.html', rows=rows)


@quiz_bp.route('/add_question', methods=['GET', 'POST'])
@login_required
def add_question():
    if request.method == 'POST':
        title = request.form.get("qname")
        question = parse_input(request.form.get("question"))
        course = request.form.get("cname")
        make_table(title, course, question)


    return render_template('add_question.html')

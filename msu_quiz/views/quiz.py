from msu_quiz.models.models import MCQ, Question, Quiz, User
from sortedcontainers.sorteddict import SortedDict
from msu_quiz import db
from flask_login import login_required, current_user
from flask import Blueprint, redirect, render_template, session
from flask import request, url_for
from msu_quiz.utils.forms import AddQuestionForm
from collections import namedtuple
import re
from loguru import logger
import random as rand
import json


quiz_bp = Blueprint(
    'quiz', __name__,
    template_folder='templates',
    static_folder='static'
)

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
    if request.method == 'POST':
        if "practice" in request.form:
            return redirect(url_for('quiz.quiz'))
        elif "add" in request.form:
            return redirect(url_for('quiz.add_question'))
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
    # Validate login attempt
    if form.validate_on_submit():
        make_table(form.quiz.data, form.course.data, form.question.data)
        return redirect(url_for('quiz.index'))
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


def make_table(title, course, question_answer):
    # question_answer has three defs. quiz: <>, course: <>, question: <>
    # parse_questions returns namedtuple (str).question and [].answer
    user = current_user.name
    questions = parse_questions(question_answer)
    quiz = Quiz(title=title,
                course=course,
                user=user,
                no_questions=len(questions),
                ranking=0)
    for q in questions:
        logger.debug(q)
        question = None
        question = Question(question=q.question,
                            answer=q.answer[0],
                            course=course)
        for a in q.answer:
            logger.debug(a)
            question.mcqs.append(MCQ(mcq=a))
        quiz.questions.append(question)
    print(quiz)
    try:
        db.session.add(quiz)
        db.session.commit()
    except:
        db.session.rollback()
        raise
    finally:
        db.session.close()


def parse_questions(question_answer):
    regex3 = r"(^(?:\s*(?:\(*[a-eA-E]\)*\.*\s+)))"
    regex4 = r"(^\s*\d+[\.\)\s]\s+)"
    regex5 = r"(^[a-fA-F][\)\.]\s+[\s\S]+)"
    regex6 = r"(^(?!(^[a-fA-F][\)\.]\s+[\s\S]+)).*)"
    regex1 = r"(^[\t ]*[0-9]+[\)\.][\t ]+[\s\S]*?(?=^[\n\r]))"

    regex = regex1
    print(question_answer)

    matches = re.finditer(regex, question_answer, re.MULTILINE)
    quiz_list = []
    QA = namedtuple('QA', 'question answer')
    for match in matches:
        q_a = match.group(0)
        qt = []
        questions = re.findall(regex6, q_a, re.MULTILINE)
        for x in questions:
            qt.append(x[0])
        question = " ".join(qt)
        answers = re.findall(regex5, q_a, re.MULTILINE)
        answer = " ".join(answers)

        tmpr = QA(re.sub(regex4, '', question),
                  re.sub(regex3, '', answer, 0, re.MULTILINE).splitlines())
        quiz_list.append(tmpr)
    return quiz_list



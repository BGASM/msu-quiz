from msu_quiz.models.models import QuizSchema, ExamSchema, Question, Quiz, MCQinQuestion, ExamQuestion, Exam, MCQ
from msu_quiz import db
from msu_quiz.utils.parse_questions import parse_questions as pq
from flask import redirect, flash, url_for, jsonify, session, render_template
from itertools import chain
from loguru import logger
import random as rand
from pprint import pprint


def add_quiz(form=None, user=None):
    if form.validate_on_submit():
        p_q = pq(form.question.data)
        sample = dict({'user': user,
                       'title': form.quiz.data,
                       'course': form.course.data,
                       'questions': p_q,
                       'no_questions': len(p_q)})
        schema = QuizSchema()
        quiz = schema.load(schema.dump(sample))
        quiz.add_self()
        flash('You have successfully submitted a quiz!')
        return redirect(url_for('quiz.index'))
    flash('There was an error in your quiz submission.')
    return redirect(url_for('quiz.add_question'))


def create_exam(quiz_id_list=None, user=None):
    quiz_list = [Quiz.query.filter_by(id=x).first() for x in quiz_id_list]
    questions_list = [x.questions for x in quiz_list]
    q_list = list(chain(*questions_list))
    rand.shuffle(q_list)
    exam = Exam(user_id=user.id)
    for n, question in enumerate(q_list, start=1):
        mcq = question.shuffle_mcq()
        eq = ExamQuestion(question_no=n, question_id=question.id)
        for x, mc in enumerate(mcq, start=1):
            eq.mcq_list.append(MCQinQuestion(mcq_no=x, mcq_id=mc))
        exam.exam_questions.append(eq)
    exam.add_self()
    a_key = ExamSchema()
    session['exam_data'] = a_key.dump(exam)
    return url_for('quiz.exam')


def score_exam(exam):
    returned = []
    exam_id = exam.pop('exam_id')
    db_exam = Exam.query.filter_by(id=exam_id).first()
    for key, value in exam.items():
        db_question = ExamQuestion.query.filter_by(exam_id=exam_id, question_id=value['question']).first()
        db_question.ans_selected = value['selected']
        db_question.ans_correct = value['answer'] == value['selected']
        db.session.add(db_question)
        mc_list = [MCQ.query.filter_by(id=mc_id).first().mcq for mc_id in value['choices']]
        returned.append({
            'test_no': key,
            'question': Question.query.filter_by(id=value['question']).first().question,
            'answer': value['answer'],
            'selected': value['selected'],
            'mcq_order': mc_list,
            'correct': value['answer'] == value['selected']
        })
    correct = 0
    for question in returned:
        correct += 1 if question.get('correct') else 0
    score = int(correct / len(returned) * 100)
    exam_data = {'exam_id': exam_id, 'score': score, 'exam_questions': returned}
    db_exam.score = score
    db.session.add(db_exam)
    db.session.commit()
    session['exam_data'] = exam_data
    pprint(exam_data, indent=2)
    return jsonify(url_for('quiz.check'))




    for mc in index['QA']['mcqs']:
        mcqs.append([mc, db.session.query(MCQ.mcq).filter(MCQ.id == mc).first()[0]])

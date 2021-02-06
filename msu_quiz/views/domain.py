from msu_quiz.models.models import QuizSchema, Question, Exam
from msu_quiz import db
from msu_quiz.utils.parse_questions import parse_questions as pq
from flask import redirect, flash, url_for, jsonify
from sortedcontainers import SortedDict
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


class MyExam():
    def __init__(self):
        self.exam = None
        self.dump = None
        self.exam_data = None

    def create_exam(self, quiz_id_list=None, user=None):
        quiz_list = []
        exam_list = {'exam_questions': []}
        for x in quiz_id_list:
            for question, q_id in db.session.query(Question, Question.id).\
                    filter_by(quiz_id=x):
                quiz_list.append({'q_id': q_id,
                                  'mc_index': question.shuffle_mcq(),
                                  'correct': False})
        rand.shuffle(quiz_list)
        for index, question in enumerate(quiz_list, 1):
            exam_list['exam_questions'].append(
                {'question_no': index, 'question': question}
            )

        pprint(exam_list, indent=2)
        self.exam = Exam(user_id=user.id, exam_data=exam_list)
        self.exam.add_self()
        self.dump = self.exam.expand_exam()
        return url_for('quiz.exam')

    def score_exam(self, exam):
        returned = []
        exam_id = exam.pop('exam_id')
        pprint(exam, indent=2)
        db_exam, exam_data = db.session.query(Exam, Exam.exam_data).filter_by(id=exam_id).first()
        correct = 0
        newexam = {}
        for k in exam_data['exam_questions']:
            nk = str(k['question_no'])

            check = exam[nk]['answer'] == exam[nk]['selected']
            exam[nk]['correct'] = check
            q_return = db.session.query(Question.question).filter_by(id=exam[nk]['question']).first()
            exam[nk]['question'] = ''.join(q_return)
            exam[nk]['test_no'] = nk
            k['question']['correct'] = check
            k['question']['selected'] = exam[nk]['selected']
            correct += 1 if check else 0
            newexam[int(nk)] = exam[nk]
        del exam
        newexam = SortedDict(newexam)
        pprint(newexam, indent=2)
        score = int(correct / len(exam_data['exam_questions']) * 100)
        exam_data = {'exam_id': exam_id, 'score': score, 'exam_questions': newexam}
        pprint(exam_data, indent=2)
        db_exam.score = score
        db_exam.add_self()

        self.dump = exam_data
        return jsonify(url_for('quiz.check'))

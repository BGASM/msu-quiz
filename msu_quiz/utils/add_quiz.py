from msu_quiz.models.models import QuizSchema
from msu_quiz.utils.parse_questions import parse_questions as pq
from flask import redirect, flash, url_for


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


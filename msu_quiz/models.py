from sqlalchemy.orm import relationship
from . import db


class Quiz(db.Model):
    __tablename__ = 'quiz'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    course = db.Column(db.String())
    no_questions = db.Column(db.Integer)
    user = db.Column(db.String())
    ranking = db.Column(db.Integer)
    questions = relationship("Question", backref="quiz", cascade="all, delete",
                             passive_deletes=True)

    def __init__(self, title, course, user, ranking, **kwargs):
        self.title = title
        self.course = course
        self.user = user
        self.ranking = ranking
        if 'no_questions' in kwargs:
            self.no_questions = kwargs["no_questions"]

    def __repr__(self):
        return '<id {}>'.format(self.id)


class Question(db.Model):
    __tablename__ = 'question'

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id', ondelete="CASCADE"))
    question = db.Column(db.String())
    answer = db.Column(db.String())
    course = db.Column(db.String())
    mcqs = relationship("MCQ", backref="question", cascade="all, delete", passive_deletes=True)

    def __init__(self, question, answer, course, **kwargs):
        self.question = question
        self.answer = answer
        self.course = course
        if 'mcqs' in kwargs:
            self.mcqs = kwargs["mcqs"]

    def __repr__(self):
        return '<id {}>'.format(self.id)


class MCQ(db.Model):
    __tablename__ = 'MCQ'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id', ondelete="CASCADE"))
    mcq = db.Column(db.String())

    def __init__(self, mcq):
        self.mcq = mcq

    def __repr__(self):
        return '<id {}>'.format(self.id)


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String())
    password = db.Column(db.String())
    name = db.Column(db.String())
    email = db.Column(db.String())

    def __init__(self, username, password, name, **kwargs):
        self.username = username
        self.password = password
        self.name = name
        if "email" in kwargs:
            self.email = kwargs["email"]

    def __repr__(self):
        return '<id {}>'.format(self.id)


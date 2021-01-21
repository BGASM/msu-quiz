from sqlalchemy.orm import relationship
from msu_quiz import db
from flask_login import UserMixin
from loguru import logger
from werkzeug.security import generate_password_hash, check_password_hash


class Quiz(db.Model):
    __tablename__ = 'quiz'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), nullable=False)
    course = db.Column(db.String(), nullable=False)
    no_questions = db.Column(db.Integer, nullable=False)
    user = db.Column(db.String(), nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    questions = relationship("Question", backref="quiz", cascade="all, delete",
                             passive_deletes=True)

    def __repr__(self):
        return f"""<Quiz(ID: {self.id}, Title:{self.title}, Course:{self.course}, User:{self.user},
            Ranking:{self.ranking}, No_questions{self.no_questions})>"""


class Question(db.Model):
    __tablename__ = 'question'

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id', ondelete="CASCADE"))
    question = db.Column(db.String(), nullable=False)
    answer = db.Column(db.String(), nullable=False)
    course = db.Column(db.String(), nullable=False)
    mcqs = relationship("MCQ", backref="question", cascade="all, delete", passive_deletes=True)

    def __repr__(self):
        return f"""<Questions(ID:{self.id}, Quiz_id:{self.quiz_id}, Question:{self.question},
            Answer:{self.answer}, Course:{self.course})>"""


class MCQ(db.Model):
    __tablename__ = 'MCQ'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id', ondelete="CASCADE"))
    mcq = db.Column(db.String(), nullable=False)

    def check_answer(self):
        logger.debug(f'{self.mcq} is {self.question.answer}')
        correct = self.mcq == self.question.answer
        return correct

    def __repr__(self):
        return f"""<MCQ(ID:{self.id}, Question_id:{self.question_id}, mcq:{self.mcq})>"""


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')

    # User authentication information. The collation='NOCASE' is required
    # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

    # User information
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=True, unique=True)

    def set_password(self, password):
        self.password = generate_password_hash(password, method='sha256')

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

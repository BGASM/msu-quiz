from os import urandom
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from msu_quiz import db
from flask_login import UserMixin
from loguru import logger
from msu_quiz import bcrypt
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

    def get_answer(self):
        logger.debug(f'{self.mcq} is {self.question.answer}')
        correct = self.question.answer
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
    password = db.Column(db.String(255), nullable=True)

    # User information
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=True, unique=True)

    _password = db.Column(db.String(255), nullable=True)

    @hybrid_property
    def passwd(self):
        return self._password

    @passwd.setter
    def passwd(self, plaintext):
        """ Takes the plaintext and encodes it into unicode, hashes a PW, then passes the
        decoded hash to database.
        """
        self._password = bcrypt.generate_password_hash(plaintext.encode('utf8')).decode('utf8')

    def check_password(self, password):
        """ First checks if user has old SHA256 password. If a SHA256 pw returns as anything besides
        null, then we check if the password was valid. If it is valid we convert the plaintext into
        bcrypt PW, remove the old password, and commit the user to DB. Then we allow the Bcrypt
        pw hash comparison.
        """
        if self.password is not None:
            logger.critical('Old style password exists.')
            if check_password_hash(self.password, password):
                self.passwd = password
                self.password = None
                db.session.add(self)
                db.session.commit()
                logger.critical('Old style password replaced.')
            else:
                return False
        return bcrypt.check_password_hash(self._password.encode('utf8'), password.encode('utf8'))

    def __repr__(self):
        return '<User {}>'.format(self.username)

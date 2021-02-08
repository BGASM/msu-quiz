from os import urandom
from sqlalchemy.orm import relationship
from sqlalchemy_json import NestedMutableJson
from sqlalchemy.ext.hybrid import hybrid_property
from msu_quiz import db
from flask_login import UserMixin, current_user
from loguru import logger
from msu_quiz import bcrypt
from werkzeug.security import generate_password_hash, check_password_hash
import random as rand

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field, fields


class MyCustomDB:
    def add_self(self):
        db.session.add(self)
        db.session.commit()


class Exam(db.Model, MyCustomDB):
    __tablename__ = 'exam'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"))
    date = db.Column(db.DateTime(timezone=True), default=db.func.now())
    score = db.Column(db.Integer, nullable=True)
    exam_data = db.Column(NestedMutableJson)

    def expand_exam(self):
        exam_questions = []
        for q in self.exam_data['exam_questions']:
            ans, q_id, question, mcqs = db.session.query(Question.answer,
                                                         Question.id,
                                                         Question.question,
                                                         Question.mcqs
                                                         ).filter_by(
                id=q['question']['q_id']).first()
            print(ans, q_id, question, mcqs)
            mcq_list = []
            for n in q['question']['mc_index']:
                mcq_list.append({'id': mcqs[n], 'q_id': q_id})

            exam_questions.append({'question_no': q['question_no'],
                                   'question': {'answer': ans, 'id': q_id, 'question': question},
                                   'mcq_list': mcq_list})
        print(exam_questions)
        result = {'id': self.id,
                  'user_id': self.user_id,
                  'exam_questions': exam_questions}
        return result


class Quiz(db.Model, MyCustomDB):
    __tablename__ = 'quiz'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), nullable=False)
    course = db.Column(db.String(), nullable=False)
    no_questions = db.Column(db.Integer, nullable=False)
    user = db.Column(db.String(), nullable=False)
    ranking = db.Column(db.Integer, nullable=False, default=0)
    created_on = db.Column(db.DateTime(timezone=True), default=db.func.now())
    questions = relationship("Question", backref="quiz", cascade="all, delete",
                             passive_deletes=True)


    def __repr__(self):
        return f"""<Quiz(ID: {self.id}, Title:{self.title}, Course:{self.course}, User:{self.user},
            Ranking:{self.ranking}, No_questions{self.no_questions})>"""


class Question(db.Model, MyCustomDB):
    __tablename__ = 'question'

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id', ondelete="CASCADE"))
    question = db.Column(db.Text(), nullable=False)
    answer = db.Column(db.Text(), nullable=False)
    mcqs = db.Column(db.ARRAY(db.Text), nullable=False)

    def shuffle_mcq(self):
        mcq_index = list(range(0, len(self.mcqs)))
        rand.shuffle(mcq_index)
        return mcq_index

    def __repr__(self):
        return f"""<Questions(ID:{self.id}, Quiz_id:{self.quiz_id}, Question:{self.question},
            Answer:{self.answer})>"""


class User(db.Model, MyCustomDB, UserMixin):
    __tablename__ = 'user'
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
    last_on = db.Column(db.DateTime(timezone=True))
    created_on = db.Column(db.DateTime(timezone=True), default=db.func.now())

    exams = relationship("Exam", backref="user", cascade="all, delete",
                         passive_deletes=True)

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
        check = False
        if self.password is not None:
            logger.critical('Old style password exists.')
            if check_password_hash(self.password, password):
                self.passwd = password
                self.password = None
                db.session.add(self)
                db.session.commit()
                logger.critical('Old style password replaced.')
            else:
                return check
        try:
            check = bcrypt.check_password_hash(self._password.encode('utf8'), password.encode('utf8'))
        except:
            logger.critical('Error in password check.')
        finally:
            return check

    def update_last_on(self):
        self.last_on = db.func.now()
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<User {}>'.format(self.username)


class QuestionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Question
        include_relationships = True
        include_fk = True
        load_instance = True
        sqla_session = db.session


class QuizSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Quiz
        include_relationships = True
        load_instance = True
        sqla_session = db.session

    questions = fields.Nested(QuestionSchema, many=True)


class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_relationships = True
        load_instance = True
        sqla_session = db.session
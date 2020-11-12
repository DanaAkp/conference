from flask import request

from flask import Flask, render_template, url_for, redirect, flash
from flask_security import SQLAlchemyUserDatastore, Security
from flask_sqlalchemy import SQLAlchemy
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin
from flask_bootstrap3 import Bootstrap
from flask_migrate import Migrate
from flask_babelex import Babel
import mimetypes
import os

from jinja2 import Template
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, SubmitField


app = Flask(__name__)
FLASK_ENV = os.environ.get("FLASK_ENV") or 'development'
app.config.from_object('app.config.%s%sConfig' % (FLASK_ENV[0].upper(), FLASK_ENV[1:]))
app.static_folder = app.config['STATIC_FOLDER']
bootstrap = Bootstrap(app)
CSRFProtect(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
# login.login_view = 'login'
#
# babel = Babel(app)
# mimetypes.init()


# region Forms
class LoginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    submit = SubmitField('Submit')


class RegistrationForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    confirm = PasswordField('Repeat password')

    submit = SubmitField('Submit')

# endregion


# region Model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')

    def __str__(self):
        return self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    author = db.relationship('Author', backref='user')

    def set_password(self, password):
        print(1)
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        print(2)
        return check_password_hash(self.password_hash, password)

    def __str__(self):
        return self.name


class Room(db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    schedule = db.relationship('Schedule', backref='room')

    def __str__(self):
        return 'Room #' + str(self.id)


class Presentation(db.Model):
    __tablename__ = 'presentations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    text = db.Column(db.Text)
    author = db.relationship('Author', backref='presentation')
    schedule = db.relationship('Schedule', backref='presentation')

    def __str__(self):
        return self.name


class Schedule(db.Model):
    __tablename__ = 'schedule'
    date_start = db.Column(db.DateTime, nullable=False)
    id_presentation = db.Column(db.Integer, db.ForeignKey('presentations.id'), primary_key=True)
    id_room = db.Column(db.Integer, db.ForeignKey('rooms.id'), primary_key=True)

    def is_room_busy(self, date_start, id_room):
        sched = Schedule.query.filter_by(id_room=id_room).filter_by(date_start=date_start).first()
        if sched is None:
            return False
        return True


class Author(db.Model):
    __tablename__ = 'authors'
    id_presentation = db.Column(db.Integer, db.ForeignKey('presentations.id'), primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

# endregion


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


# region Admin
admin = Admin(app=app, name='Admin', template_mode='bootstrap3')


class PresenterModelView(ModelView):
    def is_accessible(self):
        return current_user.role_id == 1 and current_user.is_authenticated


class PresentationModelView(PresenterModelView):
    def get_query(self):
        query = self.session.query(User)
        query = query.join(Author, Author.id_user == current_user.id)
        return query.join(self.model, Author.id_presentation == self.model.id)


class ScheduleModelView(PresenterModelView):
    def get_query(self):
        query = self.session.query(User)
        query = query.join(Author, Author.id_user == current_user.id)
        query = query.join(Presentation, Author.id_presentation == Presentation.id)
        return query.join(self.model, self.model.id_presentation == Presentation.id)


class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.role_id == 2 and current_user.is_authenticated


admin.add_view(ModelView(Presentation, db.session))
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Role, db.session))
admin.add_view(ModelView(Author, db.session))
admin.add_view(ModelView(Room, db.session))
admin.add_view(ModelView(Schedule, db.session))
# endregion


# region View
@app.route('/')
def home():
    return render_template('index.html', title='Home')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('home'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == "POST":
        username = form.username.data
        password = form.password.data
        if User.query.filter_by(name=username).first() is None:
            new_user = User()
            new_user.name = username
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
        else:
            flash('Username is exist')
            return render_template('register.html', form=form)
    return render_template('register.html', title='Register', form=form)


@app.route('/main')
def main():
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    Session = sessionmaker(bind=engine)
    session = Session()
    query = session.query(Schedule, Presentation, Room).all()

    return render_template('schedule.html', items=query, title='Schedule')


def for_presenter():
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    Session = sessionmaker(bind=engine)
    session = Session()
    query = session.query(User, Presentation)
    query = query.join(Author, Author.id_user == User.id)
    return query.join(Presentation, Author.id_presentation == Presentation.id)


@app.route('/presenter/<username>')
@login_required
def presenter(username):
    query = for_presenter()
    return render_template('presenter.html', title='Presenter - '+username, items=query)


# @app.route('/presenter/<username>/create', methods=['GET', 'POST'])
# @login_required
# def presenter_create(username):
#     if request.method == 'GET':
#         return render_template("create.html", title='Presenter - ' + username)
#     if Presentation.query.filter_by(name=request.form.get('name')).first() is None:
#         presentation = Presentation()
#         presentation.name = request.form.get('name')
#         db.session.add(presentation)
#         db.session.commit()
#     else:
#         flash('Presentation is exist')
#         return render_template("create.html", title='Presenter - ' + username)
#     query = for_presenter()
#     return render_template('presenter.html', title='Presenter - '+username, item=query)
#
#
# @app.route('/presenter/<username>/edit/<id_>', methods=['GET', 'POST'])
# @login_required
# def presenter_edit(username, id_):
#     presentation = Presentation.query.filter_by(id=id_).first()
#     if request.method == "GET":
#         return render_template("edit.html", title='Presenter - '+username, item=presentation)
#     presentation.name = request.form.get('name')
#     db.session.commit()
#
#     query = for_presenter()
#     return render_template('presenter.html', title='Presenter - '+username, item=query)


# @app.route('/presenter/<username>/delete/<id_>', methods=['GET', 'POST'])
# # @login_required
# def presenter_edit(username, id_):
#     presentation = Presentation.query.filter_by(id=id_).first()
#     db.session.delete(presentation)
#     db.session.commit()
#
#     query = for_presenter()
#     return render_template('presenter.html', title='Presenter - '+username, item=query)

# endregion


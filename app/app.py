from flask import request

from flask import Flask, render_template, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_bootstrap3 import Bootstrap
from flask_migrate import Migrate
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_wtf import CSRFProtect
from app.forms import RegistrationForm, LoginForm


app = Flask(__name__)
FLASK_ENV = os.environ.get("FLASK_ENV") or 'development'
app.config.from_object('app.config.%s%sConfig' % (FLASK_ENV[0].upper(), FLASK_ENV[1:]))
app.static_folder = app.config['STATIC_FOLDER']
bootstrap = Bootstrap(app)
CSRFProtect(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)


from app.models import User, Presentation, Room, Role, Author, Schedule


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


admin = Admin(app=app, name='Admin', template_mode='bootstrap3')


from app.admin import PresentationModelView, AdminModelView, ScheduleModelView


admin.add_view(PresentationModelView(Presentation, db.session))
admin.add_view(AdminModelView(User, db.session))
admin.add_view(AdminModelView(Role, db.session))
admin.add_view(AdminModelView(Author, db.session))
admin.add_view(AdminModelView(Room, db.session))
admin.add_view(ScheduleModelView(Schedule, db.session))


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


def session_():
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


@app.route('/main')
def main():
    session = session_()

    query = session.query(Schedule, Presentation, Room).all()

    return render_template('schedule.html', items=query, title='Schedule')


@app.route('/presenter/<username>')
@login_required
def presenter(username):
    session = session_()

    query = session.query(User, Presentation)
    query = query.join(Author, Author.id_user == User.id)
    query = query.join(Presentation, Author.id_presentation == Presentation.id)

    return render_template('presenter.html', title='Presenter - '+username, items=query)
# endregion


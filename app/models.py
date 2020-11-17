from app.app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import UserMixin


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
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    date_start = db.Column(db.DateTime, nullable=False)
    id_presentation = db.Column(db.Integer, db.ForeignKey('presentations.id'), nullable=False)
    id_room = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)

    def is_room_busy(self, date_start, id_room):
        sched = Schedule.query.filter_by(id_room=int(id_room), date_start=datetime.strptime(date_start, '%Y-%m-%d %H:%M:%S')).first()
        if sched is None:
            return False
        return True


class Author(db.Model):
    __tablename__ = 'authors'
    id_presentation = db.Column(db.Integer, db.ForeignKey('presentations.id'), primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from app.models import Author, Presentation, User
import re


class PresenterModelView(ModelView):
    def is_accessible(self):
        return current_user.role_id == 1 and current_user.is_authenticated


class PresentationModelView(PresenterModelView):
    def get_query(self):
        query = self.session.query(self.model)
        query = query.join(Author, Author.id_presentation == self.model.id)
        return query.join(User, Author.id_user == current_user.id)


class ScheduleModelView(PresenterModelView):
    def get_query(self):
        query = self.session.query(self.model)
        query = query.join(Presentation, self.model.id_presentation == Presentation.id)
        query = query.join(Author, Author.id_presentation == self.model.id_presentation)
        query = query.join(User, Author.id_user == current_user.id)
        return query

    def on_model_change(self, form, model, is_created):
        id_room = re.findall('Room #([\d])[<^]', str(form['room']))
        date_start = re.findall('value="([\w\W]+)["^]', str(form['date_start']))
        if model.is_room_busy(date_start[0], id_room[0]):
            raise Exception('Room is busy!')


class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.role_id == 2 and current_user.is_authenticated

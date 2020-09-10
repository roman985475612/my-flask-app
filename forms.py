from wtforms import Form, StringField, TextAreaField, PasswordField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Length, Email, EqualTo, DataRequired


class RegisterForm(Form):
    name = StringField('Имя', [Length(min=1, max=50)])
    username = StringField('Имя пользователя', [Length(min=4, max=25)])
    email = EmailField('Email', [Email()])
    password = PasswordField('Пароль', [DataRequired(), EqualTo('confirm', message='Passwords do not match')])
    confirm = PasswordField('Подтверждение пароля')


class LoginForm(Form):
    username = StringField('Имя пользователя', [Length(min=4, max=25)])
    password = PasswordField('Пароль', [DataRequired()])


class ArticleForm(Form):
    title = StringField('Заголоков', [Length(min=1, max=225)])
    body = TextAreaField('Текст', [Length(min=10)])

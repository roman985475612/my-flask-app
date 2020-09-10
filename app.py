from functools import wraps

from flask import Flask
from flask import flash
from flask import redirect
from flask import request
from flask import url_for
from flask import session
from flask import logging
from flask import render_template
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Length, Email, EqualTo, DataRequired

import email_validator

from passlib.hash import sha256_crypt

import data

app = Flask(__name__)
app.secret_key = 'asdfdfalkjl'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/articles')
def articles():
    articles = data.articles()
    return render_template('articles.html', articles=articles)


@app.route('/article/<int:id>')
def article(id):
    article = data.articles()[id-1]
    return render_template('article.html', article=article)


class RegisterForm(Form):
    name = StringField('Имя', [Length(min=1, max=50)])
    username = StringField('Имя пользователя', [Length(min=4, max=25)])
    email = EmailField('Email', [Email()])
    password = PasswordField('Пароль', [DataRequired(), EqualTo('confirm', message='Passwords do not match')])
    confirm = PasswordField('Подтверждение пароля')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        print('!!! form validate')
        cur = mysql.connection.cursor()
        query = "INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)"
        params = (
            form.name.data,
            form.email.data,
            form.username.data,
            sha256_crypt.encrypt(str(form.password.data))
        )
        cur.execute(query, params)
        mysql.connection.autocommit(on=True)
        cur.close()

        session['logged_in'] = True
        session['username'] = form.username.data
        session['name'] = form.name.data

        flash('Вы успешно зарегистрированы!', 'success')
        return redirect(url_for('index'))

    return render_template('register.html', form=form)


class LoginForm(Form):
    username = StringField('Имя пользователя', [Length(min=4, max=25)])
    password = PasswordField('Пароль', [DataRequired()])


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password_candidate = form.password.data

        cur = mysql.connection.cursor()
        query = "SELECT name, password FROM users WHERE username = %s"
        result = cur.execute(query, [username])

        if result > 0:
            data = cur.fetchone()
            name = data['name']
            password = data['password']

            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = username
                session['name'] = name

                flash('Здравствуйте, {}!'.format(name), 'success')
                return redirect(url_for('dashboard'))
            else:
                app.logger.info('PASSWORD NOT MATCHED')
                flash('Неправельный логин или пароль!', 'danger')

            cur.close()
        else:
            app.logger.info('NO USER')
            flash('Неправельный логин или пароль!', 'danger')

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    name = session['name']
    session.clear()
    flash('До свидания, {}'.format(name), 'success')
    return redirect(url_for('index'))


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Вам необходима войти!', 'danger')
            return redirect(url_for('login'))
    return wrap


@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')


if __name__ == '__main__':
    app.run(debug=True)

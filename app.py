from flask import Flask
from flask import flash
from flask import redirect
from flask import request
from flask import url_for
from flask import sessions
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

        flash('Вы успешно зарегистрированы!', 'success')

        return redirect(url_for('index'))

    return render_template('register.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)

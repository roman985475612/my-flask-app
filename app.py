from flask import Flask
from flask import flash
from flask import redirect
from flask import request
from flask import url_for
from flask import session
from flask import render_template
from flask_mysqldb import MySQL

from passlib.hash import sha256_crypt

from functions import is_logged_in
from forms import RegisterForm, LoginForm, ArticleForm

app = Flask(__name__)
app.secret_key = 'asdfdfalkjl'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


@app.route('/index')
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/articles')
def articles():
    cur = mysql.connection.cursor()
    query = "SELECT * FROM articles"
    result = cur.execute(query)
    data = {}
    if result > 0:
        data = cur.fetchall()
    return render_template('articles.html', articles=data)


@app.route('/articles/<int:article_id>')
def article(article_id):
    cur = mysql.connection.cursor()
    query = "SELECT * FROM articles WHERE id=%s"
    result = cur.execute(query, [article_id])
    data = {}
    if result > 0:
        data = cur.fetchone()
    cur.close()
    return render_template('article.html', article=data)


@app.route('/articles/create', methods=['GET', 'POST'])
@is_logged_in
def article_create():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        cur = mysql.connection.cursor()
        mysql.connection.autocommit(on=True)
        query = "INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)"
        params = (
            form.title.data,
            form.body.data,
            session['username']
        )
        cur.execute(query, params)
        cur.close()
        flash('Статья добавлена', 'success')
        return redirect(url_for('dashboard'))

    return render_template('article-create.html', form=form, header='Добавление')


@app.route('/articles/<int:article_id>/update', methods=['GET', 'POST'])
@is_logged_in
def article_update(article_id):
    cur = mysql.connection.cursor()
    query = "SELECT * FROM articles WHERE id=%s"
    result = cur.execute(query, [article_id])
    article = {}
    if result > 0:
        article = cur.fetchone()
    cur.close()

    form = ArticleForm(request.form)

    if request.method == 'GET':
        form.title.data = article['title']
        form.body.data = article['body']
    elif request.method == 'POST' and form.validate():
        cur = mysql.connection.cursor()
        mysql.connection.autocommit(on=True)
        query = """ UPDATE articles 
                    SET title=%s, body=%s 
                    WHERE id=%s """
        params = (
            form.title.data,
            form.body.data,
            article_id
        )
        cur.execute(query, params)
        cur.close()
        flash('Статья обновлена', 'success')
        return redirect(url_for('dashboard'))

    return render_template('article-create.html', form=form, header='Редактирование')


@app.route('/articles/<int:article_id>/delete', methods=['GET', 'POST'])
@is_logged_in
def article_delete(article_id):
    cur = mysql.connection.cursor()
    mysql.connection.autocommit(on=True)
    cur.execute("DELETE FROM articles WHERE id=%s", [article_id])
    cur.close()
    flash('Статья удалена', 'success')
    return redirect(url_for('dashboard'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
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
@is_logged_in
def logout():
    name = session['name']
    session.clear()
    flash('До свидания, {}'.format(name), 'success')
    return redirect(url_for('index'))


@app.route('/dashboard')
@is_logged_in
def dashboard():
    cur = mysql.connection.cursor()
    query = "SELECT * FROM articles"
    result = cur.execute(query)
    data = {}
    if result > 0:
        data = cur.fetchall()
    return render_template('dashboard.html', articles=data)


if __name__ == '__main__':
    app.run(debug=True)

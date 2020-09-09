from flask import Flask
from flask import render_template

import data

app = Flask(__name__)


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


if __name__ == '__main__':
    app.run(debug=True)

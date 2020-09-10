from functools import wraps

from flask import session
from flask import url_for
from flask import flash
from flask import redirect


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Вам необходима войти!', 'danger')
            return redirect(url_for('login'))
    return wrap

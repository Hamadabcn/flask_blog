import functools
from flask import Blueprint, request, redirect, render_template, url_for, flash, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from blog import get_db

bp = Blueprint('auth', __name__)


def login_required(func):
    @functools.wraps(func)
    def wrappend_func(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return func(**kwargs)
    return wrappend_func


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        error = None

        if not username:
            error = 'Username Required'

        if not email:
            error = 'Email Required'

        if not password:
            error = 'Password Required'

        if error is None:
            db = get_db()

            try:
                db.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, generate_password_hash(password)))
                db.commit()
                db.close()
            except db.IntegrityError:
                error = f'{username} is already registered'
            else:
                return redirect(url_for('login'))
            flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        error = None
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

        if not email:
            error = 'Invalid Email'
        elif not check_password_hash(user['password'], password):
            error = 'Invalid Password'

        if error is None:
            session.clear()
            session['user_id'] = user['Field1']
            return redirect(url_for('blog.index'))  # Update the endpoint to 'blog.index'

        flash(error)

    if g.user:
        return redirect(url_for('blog.index'))  # Update the endpoint to 'blog.index'
    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute('SELECT * FROM users WHERE Field1 = ?', (user_id,)).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('blog.index'))  # Update the endpoint to 'blog.index'

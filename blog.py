from flask import render_template, request, url_for, redirect, Blueprint, session, g, flash, abort
import sqlite3
import functools


DATABASE = 'block.db'

bp = Blueprint('blog', __name__, url_prefix='/posts')


def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


def login_required(func):
    @functools.wraps(func)
    def wrappend_func(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return func(**kwargs)
    return wrappend_func


def get_post(post_id):
    post = get_db().execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()

    if post is None:
        abort(404, f'The Article with the identifier {post_id} not found')

    if post['author_id'] != g.user['Field1']:
        print(post['author_id'])
        print(g.user['Field1'])
        abort(403)

    return post


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        # Corrected the column name to 'id'
        g.user = get_db().execute('SELECT * FROM users WHERE Field1 = ?', (user_id,)).fetchone()


@bp.route('/')
@login_required
def index():
    connection = get_db()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)


@bp.route('/<int:post_id>')
def show(post_id):
    connection = get_db()
    post = connection.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    return render_template('show.html', post=post)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        connection = get_db()
        title = request.form['title']
        body = request.form['body']
        # Assuming your posts table has 'title', 'body', and 'author_id' columns
        connection.execute('INSERT INTO posts (title, body, author_id) VALUES (?, ?, ?)', (title, body, g.user['Field1']))
        connection.commit()
        connection.close()
        return redirect(url_for('blog.index'))
    return render_template('create.html')


@bp.route('/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update(post_id):
    post = get_post(post_id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required'

        if error is not None:
            flash(error)
        else:
            # Check if the current user is the author of the post
            if post['author_id'] != g.user['Field1']:
                abort(403)  # User does not have permission to update this post

            db = get_db()
            db.execute('UPDATE posts SET title = ?, body = ? WHERE id = ?', (title, body, post_id))
            db.commit()
            db.close()
            return redirect(url_for('blog.index'))

    return render_template('create.html', post=post)

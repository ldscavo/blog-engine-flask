from blog import app
from blog.models import *
from flask import render_template, flash, session, request, \
        redirect, url_for
from sqlalchemy.sql import extract, desc
import hashlib
from datetime import datetime

@app.context_processor
def utility_processor():
    year = datetime.now().year
    posts = Post.query.order_by(desc(Post.pub_date)).limit(3)
    return dict(current_year=year, recent_posts=posts)

@app.route('/', endpoint='index')
def index():
    return page(1)

@app.route('/page/<int:page>')
def page(page):
    posts = Post.query.order_by(desc(Post.pub_date)).paginate(page, per_page=3)

    return render_template('page.html', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password_hashed = hashlib.sha512(request.form['password']).hexdigest()
        user = User.query.filter_by(username=request.form['username'],
                passwordhash=password_hashed).first()
        if user is not None:
            session['user_id'] = user.id
            flash('You have successfully logged in!')
            return redirect(url_for('index'))
        else:
            flash('Username or password is not correct!')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have successfully logged out.')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.form['password'] != request.form['password-confirm']:
            flash('Passwords do not match.')
            return render_template('register.html')
        user = User(request.form['username'],
                request.form['email'],
                request.form['password'])
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id

        flash('You have been registered!')
        return redirect(url_for('index'))

    return render_template('register.html')

@app.route('/<int:year>/<int:month>/<int:day>/<string:slug>')
def post(year, month, day, slug):
    post = Post.query.filter(
            extract('year', Post.pub_date) == year,
            extract('month', Post.pub_date) == month,
            extract('day', Post.pub_date) == day,
            Post.slug == slug).first_or_404()
    
    return render_template('post.html', post=post)

@app.route('/post/<int:post_id>')
def post_by_id(post_id):
    post = Post.query.filter(Post.id == post_id).first_or_404()

    return render_template('post.html', post=post)

@app.route('/posts/new', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        post = Post(session['user_id'],
                request.form['title'],
                request.form['body'])
        db.session.add(post)
        db.session.commit()

        flash('Published successfully!')
        return redirect(url_for('index'))

    return render_template('new_post.html')

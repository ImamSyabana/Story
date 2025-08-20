from datetime import date
from flask import abort, render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user, login_required
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from bs4 import BeautifulSoup

from app import app, db, gravatar
from app.models import User, BlogPost, Comment
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm

# Custom decorator for admin-only routes
def admin_only(func):
    @wraps(func)
    def wrapper_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.id != 1:
            return abort(403)
        return func(*args, **kwargs)
    return wrapper_function

@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        user_to_register = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if user_to_register:
            flash('You have signed up with that email, log in instead.', 'error')
            return redirect(url_for('login'))
        
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8)
        new_user = User(
            email=email,
            password=hashed_password,
            name=form.name.data
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('get_all_posts'))
    return render_template("register.html", form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user_to_login = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if not user_to_login:
            flash('That email does not exist. Please try again.', 'error')
            return redirect(url_for('login'))
        elif not check_password_hash(user_to_login.password, password):
            flash('Password Incorrect. Please try again.', 'error')
            return redirect(url_for('login'))
        else:
            login_user(user_to_login)
            return redirect(url_for("get_all_posts"))
    return render_template("login.html", form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))

@app.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts)

@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    form = CommentForm()
    requested_post = db.get_or_404(BlogPost, post_id)
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('You need to login or register to comment.', 'error')
            return redirect(url_for('login'))
        
        new_comment = Comment(
            author_id=current_user.id,
            text=form.text.data,
            post_id=post_id
        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('show_post', post_id=post_id))
    
    return render_template("post.html", post=requested_post, comment_form=form)

@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)

@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)

@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")
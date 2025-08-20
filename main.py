from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user,login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, ForeignKey
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
# Import your forms from the forms.py
from forms import CreatePostForm
from forms import RegisterForm, LoginForm, CommentForm
from bs4 import BeautifulSoup

'''
Make sure the required packages are installed: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from the requirements.txt for this project.
'''

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap5(app)

# TODO: Configure Flask-Login
# initiate login manager object
login_manager = LoginManager()
# conect login manager dengan app
login_manager.init_app(app)

#Set the login view: Flask-Login will redirect unauthenticated users to this route.
login_manager.login_view = "login"



# Assuming you have a User model (nama databasenya User). It must inherit from UserMixin.
# class User(UserMixin, db.Model):
#     ...

@login_manager.user_loader
def load_user(id):
    if id:
        return db.get_or_404(User, int(id))
    return None

# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# create gravatar 
gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)

# TODO: Create a User table for all your registered users. 
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))

    # This will act like a List of BlogPost objects attached to each User.
    # The "author" property in BlogPost is a reference to the User object.
    posts: Mapped[list["BlogPost"]] = relationship(back_populates="author")

    
    comments: Mapped[list["Comment"]] = relationship(back_populates="author")

# CONFIGURE TABLES
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)

    #author: Mapped[str] = mapped_column(String(250), nullable=False)

    # Create a relationship to the User object.
    # The "posts" property in User is a reference to this relationship.
    author: Mapped["User"] = relationship(back_populates="posts")

    # Create the foreign key. This will connect blog_posts table to the users table.
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    img_url: Mapped[str] = mapped_column(String(250), nullable=False)

# Create a comment table
class Comment(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    author: Mapped["User"] = relationship(back_populates="comments")
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    post_id: Mapped[int] = mapped_column(ForeignKey("blog_posts.id"))


with app.app_context():
    db.create_all()


# TODO: Use Werkzeug to hash the user's password when creating a new user.
@app.route('/register', methods = ["GET", "POST"])
def register():
    form = RegisterForm()

    if request.method == "POST":
        # mengambil yang ada di kolom input HTML
        name = form.name.data
        email = form.email.data

        # convert password menjadi hash + salt
        password = form.password.data
        password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        
        user_to_register = db.session.execute(db.select(User).where(User.email == email)).scalar()
        
        # kalo email sudah exist maka user_to_register ada isinya 
        # berarti ngga boleh register
        if user_to_register:
            # Handle existed credentials
            flash('You have signed up with that email, log in instead.', 'error')
            return redirect(url_for('login'))
        
        # kalo email belum exist berarti user_to_register return None
        # berarti email belum pernah dipake dan boleh register.
        elif not(user_to_register):
            # menyiapkan records object USER untuk dimasukkan ke database
            new_user = User(
                email = email,
                password = password,
                name = name
            )

            # menambahkan data ke datatbase.
            db.session.add(new_user)
            db.session.commit()
            
            # login the new user
            login_user(new_user)

            return redirect(url_for('get_all_posts'))
    return render_template("register.html", form = form)


# TODO: Retrieve a user from the database based on their email. 
@app.route('/login', methods = ["GET", "POST"])
def login():
    form = LoginForm()

    if request.method == "POST":
        # mengambil yang ada di kolom input HTML
        email = form.email.data
        password = form.password.data

        # mengambil data user yang ada di database
        user_to_login = db.session.execute(db.Select(User).where(User.email == email)).scalar()

        # Login and validate the user.
        # user should be an instance of your `User` class
        # Check if the user exists and the password is correct
        if not(user_to_login):
            # Handle invalid credentials
            flash('That email does not exist. Please try again.', 'error')
            return redirect(url_for('login'))
        elif check_password_hash(user_to_login.password, password) == False:
            # Handle invalid credentials
            flash('Password Incorrect. Please try again.', 'error')
            return redirect(url_for('login'))
        else:
            #flash('You were successfully logged in!', 'success')
            login_user(user_to_login)
            return redirect(url_for("get_all_posts"))
        
    return render_template("login.html", form = form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))

def admin_only(func):
    @wraps(func)
    def wrapper_function(*args, **kwargs):
        if current_user.is_authenticated:
            if current_user.id ==1:
                return func(*args, **kwargs)
            else: 
                abort(403)
    return wrapper_function

@app.route('/')
def get_all_posts():
    # data yang ada di tabel blog_posts
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()

    # data yang ada di tabel user
    
    user_results = db.session.execute(db.Select(User))
    users = user_results.scalars().all()

    return render_template("index.html", all_posts=posts, users = users)


# TODO: Allow logged-in users to comment on posts
@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    form = CommentForm()

    if form.validate_on_submit():
        if current_user.is_authenticated:
            comment_input = Comment(
                author_id = current_user.id,
                text = form.text.data,
                post_id = post_id
            )

            db.session.add(comment_input)
            db.session.commit()
            #return redirect(url_for("get_all_posts"))

        else:
            flash('You need to login or register to comment.', 'error')
            return redirect(url_for('login'))

    # show all who comment on the post 
    commenters = db.session.execute(db.select(Comment).where(Comment.post_id == post_id)).scalars().all()

    # Show all comments related to the post
    post_comments = db.session.execute(db.select(Comment).where(Comment.post_id == post_id)).scalars().all()
    wo_html_post_comments = []
    for post in (post_comments):
        cleaned_text = BeautifulSoup(post.text, "html.parser").get_text()
        wo_html_post_comments.append({'author': post.author, 'text': cleaned_text})

    requested_post = db.get_or_404(BlogPost, post_id)
    return render_template("post.html", post=requested_post, comment_form = form, comment_text = wo_html_post_comments)


# TODO: Use a decorator so only an admin user can create a new post
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


# TODO: Use a decorator so only an admin user can edit a post
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
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)


# TODO: Use a decorator so only an admin user can delete a post
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


if __name__ == "__main__":
    app.run(debug=True, port=5002)

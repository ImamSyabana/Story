from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap5
from flask import Flask, render_template, redirect, url_for
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

# WTForm for creating a blog post
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


# TODO: Create a RegisterForm to register new users
class RegisterForm(FlaskForm):
    email = StringField(label = "Email", validators = [DataRequired()])
    name = StringField(label = "Name", validators = [DataRequired()])
    password = PasswordField(label = "Password", validators = [DataRequired()])
    submit = SubmitField('SIGN ME UP!')



@app.route("/register", methods = ["GET", "POST"])
def regist_user():
    pass
    

# TODO: Create a LoginForm to login existing users
#Create a LoginForm to login existed users
class LoginForm(FlaskForm):
    email = StringField(label = "Email", validators = [DataRequired()])
    password = PasswordField(label = "Password", validators = [DataRequired()])
    submit = SubmitField('LET ME IN!')

# TODO: Create a CommentForm so users can leave comments below posts
class CommentForm(FlaskForm):
    text = CKEditorField(label = 'Comment', validators=[DataRequired()])
    submit = SubmitField('SUBMIT COMMENT')
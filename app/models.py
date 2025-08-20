from app import db
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, ForeignKey
from flask_login import UserMixin

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


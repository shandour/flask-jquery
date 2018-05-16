# -*- coding: utf-8 -*-
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin
from sqlalchemy import func
from sqlalchemy.orm import column_property


db = SQLAlchemy()


authors_books = db.Table(
    'authors_books',
    db.Column('author_id', db.Integer, db.ForeignKey('authors.id'),
              primary_key=True),
    db.Column('books_id', db.Integer, db.ForeignKey('books.id'),
              primary_key=True))


class Author(db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    surname = db.Column(db.String(100))
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    books = db.relationship('Book', secondary=authors_books,
                            backref='authors')

    fullname = column_property(surname + name)

    def __repr__(self):
        return ("<Author id={id}, name: {name}, surname: {surname}"
                ", description: '{description}...'>").format(
                    id=self.id,
                    name=self.name,
                    surname=self.surname
                    if self.surname else '',
                    description=self.description[:20]
                        if self.description
                        else '')


class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(1000), index=True)
    text = db.Column(db.Text)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return ("<Book id={id}, title: {title}, description: '{description}"
                ", text: '{text}...'>").format(
                    id=self.id, title=self.title,
                    description=self.description[:20]
                        if self.description
                        else '',
                    text=self.text[:25])


# security functionality
users_roles = db.Table(
    'users_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'),
              primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'),
              primary_key=True))


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(130))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime(), default=datetime.utcnow)
    roles = db.relationship('Role', secondary=users_roles,
                            backref='users')

    books = db.relationship('Book', backref='user')
    authors = db.relationship('Author', backref='user')

    def __repr__(self):
        return "<User id={id}, username: {username}, email: {email}>".format(
            id=self.id, username=self.username, email=self.email
        )


class Role(db.Model, RoleMixin):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(200))

    def __repr__(self):
        return "<Role id={id}, name: {name}>, description: {description}>"\
            .format(id=self.id, name=self.name,
                    description=self.description
                        if self.description
                        else '')


# full-text search indices
db.Index('idx_authors_name_full_text_search',
         func.to_tsvector('simple', Author.name),
         func.to_tsvector('simple', Author.surname),
         postgresql_using='gin')
db.Index('idx_fullname_text_search',
         func.to_tsvector('simple', Author.fullname),
         postgresql_using='gin')
db.Index('idx_books_title_full_text_search',
         func.to_tsvector('simple', Book.title),
         postgresql_using='gin')

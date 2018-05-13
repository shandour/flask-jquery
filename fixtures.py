# -*- coding: utf-8 -*-
from string import ascii_letters

from random import choice, randint

from loremipsum import get_paragraphs

from projecto.models import (
    db,
    Author,
    Book,
    User
)


def create_fixtures(creation_iteration_number=100, users_number=10):
    if creation_iteration_number < 1:
        return

    user_list = create_users_list(users_number)

    object_list = [Author(
        name='Lolko',
        surname='Lolkun',
        description='simply da greatest',
        user=user_list[0],
        books=[
            Book(
                title='Lel Book',
                description=return_random_text(1, 3),
                text=return_random_text(1, 20),
                user=user_list[0]
            )
        ]
    )]

    while creation_iteration_number > 0:
        author = Author(
            name=return_random_string(5, 50),
            surname=return_random_string(0, 50),
            description=return_random_string(10, 200),
            user=choice(user_list)
        )

        book_list = []

        for x in range(randint(1, 10)):
            book_list.append(Book(
                title=return_random_string(2, 50),
                description=return_random_text(1, 3),
                text=return_random_text(1, 20),
                user=choice(user_list)
            ))

        author.books = book_list

        object_list.append(author)
        creation_iteration_number -= 1

    db.session.add_all(object_list)
    db.session.commit()


def return_random_string(min_letters, max_letters):
    return (
        "".join(choice(ascii_letters)
                for x in range(randint(min_letters, max_letters)))
        .capitalize()
    )


def return_random_text(min_paragraphs, max_paragraphs):
    return " ".join(get_paragraphs(randint(min_paragraphs, max_paragraphs)))


def create_users_list(users_number):
    user_name_set = set()
    while len(user_name_set) < users_number:
        user_name_set.add(return_random_string(1, 50))
    user_name_list = list(user_name_set)

    user_list = [User(
            username='vova',
            email='vova@vova.vova',
            password='Mynameisvova',
            active=True)]

    iteration = 0
    while iteration < users_number:
        username = user_name_list[iteration]
        email = username + '@supermail.mail'
        user_list.append(
            User(
                username=username,
                email=email,
                password=return_random_string(10, 107),
                active=True
            )
        )
        iteration += 1

    db.session.add_all(user_list)
    db.session.flush()

    return user_list

# -*- coding: utf-8 -*-
from sortedcontainers import SortedDict, SortedListWithKey, SortedList
from sqlalchemy import func
from sqlalchemy.orm import joinedload

from projecto.models import Author, Book, db


def get_authors_count():
    return Author.query.count()


def get_all_authors_with_sections():
    """Returns a SortedDict of last name letters of corresponding authors"""
    authors = Author.query.all()

    d = SortedDict()
    for a in authors:
        first_letter = a.fullname[0].upper()
        if first_letter not in d:
            d[first_letter] = {
                'items': SortedListWithKey(
                    key=lambda a: (
                        (a['surname'] + a['name']).lower()
                        if a['surname']
                        else a['name'].lower()))
            }
        d[first_letter]['items'].add({'id': a.id,
                                      'name': a.name,
                                      'surname': a.surname})
    return d


def get_author_by_id(id=None):
    """Returns an author by id or aborts with 404"""
    author = Author.query.get_or_404(id)
    return author


def find_authors(name=None, surname=None, book_title=None):
    if not (name or surname or book_title):
        return None
    authors_query = Author.query
    if name:
        authors_query = authors_query.filter(
            func.to_tsvector('simple', Author.name)
                .match(name + ':*', postgresql_regconfig='simple'))
    if surname:
        authors_query = authors_query.filter(
            func.to_tsvector('simple', Author.surname)
                .match(surname + ':*', postgresql_regconfig='simple'))
    if book_title:
        authors_query = authors_query\
            .join(Author.books)\
            .filter(
                func.to_tsvector('simple', Book.title)
                    .match(book_title + ':*', postgresql_regconfig='simple'))
    return authors_query.order_by(Author.surname.asc(), Author.name.asc())


def get_book_by_id(id=None):
    """Returns a book by id or aborts with 404"""
    book = Book.query.get_or_404(id)
    return book


def get_books_count():
    return Book.query.count()


def get_all_books_with_sections():
    """Returns a SortedDict of first name letters of corresponding books"""
    books = Book.query\
        .options(joinedload(Book.authors))\
        .order_by(Book.title.asc())\
        .all()

    d = SortedDict()
    for b in books:
        first_letter = b.title[0].upper()

        if first_letter not in d:
            d[first_letter] = {'items': []}

        d[first_letter]['items'].append(
            {
                'id': b.id,
                'title': b.title,
                'authors': SortedList(
                    [str(a.surname + ' ' + a.name)
                     if a.surname else a.name
                     for a in b.authors])
            })
    return d


def get_entities_for_letter(entity_type,
                            max_entities_per_page,
                            letter=None,
                            page=None):
    if entity_type == 'books':
        if not letter:
            return

        app_limit = max_entities_per_page
        if Book.query.count() > app_limit:
            limit = app_limit
        else:
            limit = None
        offset = (int(page) - 1) * app_limit if page else None

        books = Book.query\
            .options(joinedload(Book.authors))\
            .filter(func.to_tsvector('simple', Book.title)
                        .match(letter + ':*', postgresql_regconfig='simple'))\
            .order_by(Book.title.asc())\
            .limit(limit)\
            .offset(offset)\
            .all()

        finished = True if len(books) < app_limit else False

        return {letter.upper(): {
            'items': [
                {
                    'id': book.id,
                    'title': book.title,
                    'authors': list(SortedList(
                        [str(a.surname + ' ' + a.name)
                         if a.surname else a.name
                         for a in book.authors]))
                } for book in books
            ],
            'finished': finished}
        }
    elif entity_type == 'authors':
        if not letter:
            return

        app_limit = max_entities_per_page
        if Author.query.count() > app_limit:
            limit = app_limit
        else:
            limit = None
        offset = (int(page) - 1) * app_limit if page else None

        authors = Author.query\
            .filter(func.to_tsvector('simple', Author.fullname)
                        .match(letter + ':*', postgresql_regconfig='simple'))\
            .order_by(Author.fullname.asc())\
            .limit(limit)\
            .offset(offset)\
            .all()

        finished = True if len(authors) < app_limit else False

        return {letter.upper(): {
            'items': [
                {
                    'id': author.id,
                    'name': author.name,
                    'surname': author.surname
                } for author in authors
            ],
            'finished': finished}
        }


def add_book(form):
    new_book = Book()
    new_book.title = form.title.data
    new_book.text = form.text.data

    if form.description:
        new_book.description = form.description.data

    new_book.authors = Author.query\
        .filter(Author.id.in_(
            [int(a) for a in form.authors.data]))\
        .all()

    db.session.add(new_book)
    db.session.commit()


def update_book(book_id, form):
    book = Book.query.get_or_404(book_id)
    book.title = form.title.data
    book.authors = Author.query\
        .filter(Author.id.in_(
            [int(a) for a in form.authors.data]))\
        .all()
    book.description = form.description.data
    book.text = form.text.data

    db.session.commit()


def add_author(form):
    new_author = Author()

    new_author.name = form.first_name.data
    if form.last_name.data:
        new_author.surname = form.last_name.data
    if form.description.data:
        new_author.description = form.description.data
    if form.books:
        for book in form.books:
            if book.title.data and book.content.data:
                new_book = Book()
                new_book.title = book.title.data
                new_book.text = book.content.data
                if book.overview.data:
                    new_book.description = book.overview.data
                new_author.books.append(new_book)

    db.session.add(new_author)
    db.session.commit()


def update_author(author_id, form):
    author = Author.query.get_or_404(author_id)
    author.name = form.name.data
    author.surname = form.surname.data
    author.books = Book.query\
        .filter(Book.id.in_(
            [int(b) for b in form.books.data]))\
        .all()
    author.description = form.description.data

    db.session.commit()


def get_authors_autocomplete(query, chunk, suggestions_per_query):
    limit = suggestions_per_query
    offset = limit * (int(chunk) - 1)

    entity_list = db.session\
        .query(Author.id, Author.surname, Author.name)\
        .filter((func.to_tsvector('simple', Author.name))
                .match(query + ':*') |
                (func.to_tsvector('simple', Author.surname))
                .match(query + ':*'))\
        .order_by(func.ts_rank(func.to_tsvector('simple', Author.name),
                               (query + ':*')))\
        .offset(offset)\
        .limit(limit)\
        .all()

    finished = True if len(entity_list) < limit else False

    authors = [
        {'id': a.id,
         'name': ((a.surname + ' ' + a.name).strip()
                  if a.surname
                  else a.name)}
        for a in entity_list]
    return {'results': authors, 'finished': finished}


def get_books_autocomplete(query, chunk, suggestions_per_query):
    limit = suggestions_per_query
    offset = limit * (int(chunk) - 1)

    entity_list = db.session\
        .query(Book.id, Book.title)\
        .filter((func.to_tsvector('simple', Book.title))
                .match(query + ':*'))\
        .order_by(func.ts_rank(func.to_tsvector('simple', Book.title),
                               (query + ':*')))\
        .offset(offset)\
        .limit(limit)\
        .all()

    finished = True if len(entity_list) < limit else False

    books = [
        {'id': b.id,
         'title': b.title}
        for b in entity_list]
    return {'results': books, 'finished': finished}


def check_if_author_exists(author_ids):
    authors_count = db.session\
        .query(func.count(Author.id))\
        .filter(Author.id.in_(author_ids))\
        .scalar()
    return len(author_ids) == authors_count


def delete_entity(entity):
    db.session.delete(entity)
    db.session.commit()

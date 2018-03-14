from string import ascii_uppercase

from flask import (
    render_template,
    current_app as app,
    redirect,
    url_for,
    request,
    flash,
    jsonify,
    g,
    abort,
    Response
)
from flask_sqlalchemy import Pagination
from flask_security import login_required, roles_accepted, current_user

from projecto.forms import (
    AuthorsSearchForm,
    AddBookForm,
    AddAuthorForm,
    EditAuthorForm)
from projecto.db_operations import (
    get_all_authors_with_sections,
    get_all_books_with_sections,
    get_entities_for_letter,
    get_author_by_id,
    get_book_by_id,
    get_random_entity,
    get_authors_autocomplete,
    get_books_autocomplete,
    find_authors,
    add_book,
    add_author,
    update_book,
    update_author,
    delete_entity as delete_db_entity)
from projecto.security import ADMIN_ROLE, EDITOR_ROLE
from projecto.frontend import frontend_bp


@frontend_bp.route('/')
def index():
    return render_template('index.html')


@frontend_bp.route('/books')
def books():
    return render_template('books.html')


@frontend_bp.route('/links')
def links():
    return render_template('links.html')


@frontend_bp.route('/about')
def about():
    return render_template('about.html')


# books views
@frontend_bp.route('/books/show/<int:book_id>')
def show_book(book_id=None):
    book = get_book_by_id(book_id)
    return render_template('show_book.html', book_id=book_id, book=book)


@frontend_bp.route('/books/show-all')
@frontend_bp.route('/books/show-all/<string:letter>')
def show_all_books(letter=None):
    g.ascii = ascii_uppercase
    max_entities = app.config['MAX_ENTITIES_PER_CORPUS_PAGE']
    if not letter:
        books = get_all_books_with_sections(max_entities)
        if books:
            return render_template('b_corpus.html', books=books, lettering=False)
        else:
            letter = 'A'
    books = get_entities_for_letter('books', max_entities, letter)
    return render_template('b_corpus.html', books=books, lettering=True)


@frontend_bp.route('/api/get-entities')
def get_entities():
    letter = request.args.get('letter')
    chunk = request.args.get('chunk')
    entity_type = request.args.get('type')
    max_entities = app.config['MAX_ENTITIES_PER_CORPUS_PAGE']

    items = get_entities_for_letter(entity_type, max_entities, letter, chunk)
    return jsonify(items)


@frontend_bp.route('/books/add', methods=['GET', 'POST'])
@login_required
def add_books():
    form = AddBookForm(request.form)
    if request.method == "POST" and form.validate_on_submit():
        add_book(form)
        return redirect(url_for('frontend.books'))
    return render_template('add_book.html', form=form)


@frontend_bp.route('/books/edit/<int:book_id>', methods=['GET', 'POST'])
@login_required
def edit_book(book_id=None):
    book = get_book_by_id(book_id)
    extended_roles_checker(book)

    if request.method == "GET":
        form = AddBookForm(obj=book)
        authors_array = [
            {
                'id': a.id,
                'name': (a.surname + ' ' + a.name
                         if a.surname
                         else a.name)
            }
            for a in book.authors
        ]

    if request.method == "POST":
        form = AddBookForm(request.form)
        if form.validate_on_submit():
            update_book(book_id, form)
            return redirect(url_for('frontend.books'))

        if len(form.authors.data[0].strip()) > 0:
            authors_array = []
            for a in form.authors.data:
                a_id = a
                auth = get_author_by_id(a)
                a_name = (auth.surname + ' ' + auth.name
                          if auth.surname
                          else auth.name)
                authors_array.append({'id': a_id, 'name': a_name})
        else:
            authors_array = []
    return render_template(
        'edit_book.html',
        book_id=book_id,
        form=form,
        book=book,
        authors_array=authors_array)


@frontend_bp.route('/books/random')
def random_books():
    book_id = get_random_entity("book")

    return redirect(url_for('frontend.show_book', book_id=book_id))


# author views

@frontend_bp.route('/authors', methods=['GET'])
@frontend_bp.route('/authors/<int:page>', methods=['GET'])
def authors(page=None):
    form = AuthorsSearchForm()
    pagination = None
    per_page = app.config['SEARCH_PAGINATION_PER_PAGE']
    g.query = None

    if len(request.args.values()):
        form = AuthorsSearchForm(request.args)
        g.query = ('&'.join('{}={}'.format(k, v)
                            for k, v in request.args.iteritems()))
        if form.validate():
            authors = find_authors(**form.data)
            if not authors:
                pagination = Pagination(*[None for i in range(5)])
            else:
                pagination = authors.paginate(page, per_page)

    return render_template('authors.html', form=form, pagination=pagination)


@frontend_bp.route('/authors/show-all')
@frontend_bp.route('/authors/show-all/<string:letter>')
def show_all_authors(letter=None):
    g.ascii = ascii_uppercase
    max_entities = app.config['MAX_ENTITIES_PER_CORPUS_PAGE']
    if not letter:
        authors = get_all_authors_with_sections(max_entities)
        if authors:
            return render_template(
                'corpus.html',
                authors=authors,
                lettering=False)
        else:
            letter = 'A'
    authors = get_entities_for_letter('authors', max_entities, letter)
    return render_template('corpus.html', authors=authors, lettering=True)


@frontend_bp.route('/authors/show/<int:author_id>')
def show_author(author_id=None):
    author = get_author_by_id(author_id)
    return render_template('show_author.html', author_id=author_id,
                           author=author)


@frontend_bp.route('/authors/add', methods=['GET', 'POST'])
@login_required
def add_authors():
    form = AddAuthorForm(request.form)
    if request.method == "POST" and form.validate_on_submit():
        add_author(form)
        return redirect(url_for('frontend.authors'))
    return render_template('add_author.html', form=form)


@frontend_bp.route('/authors/edit/<int:author_id>', methods=['GET', 'POST'])
@login_required
def edit_author(author_id=None):
    author = get_author_by_id(author_id)
    extended_roles_checker(author)

    if request.method == "GET":
        form = EditAuthorForm(obj=author)
        books_array = [
            {
                'id': b.id,
                'title': b.title
            }
            for b in author.books
        ]

    if request.method == "POST":
        form = EditAuthorForm(request.form)
        if form.validate_on_submit():
            update_author(author_id, form)
            return redirect(url_for('frontend.authors'))

        if len(form.books.data[0].strip()) > 0:
            books_array = []
            for b in form.books.data:
                b_id = b
                bk = get_book_by_id(b)
                b_title = bk.title
                books_array.append({'id': b_id, 'title': b_title})
        else:
            books_array = []
    return render_template(
        'edit_author.html',
        author_id=author_id,
        form=form,
        author=author,
        books_array=books_array)


@frontend_bp.route('/authors/random')
def random_authors():
    author_id = get_random_entity("author")

    return redirect(url_for('frontend.show_author', author_id=author_id))


# error handler
@frontend_bp.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@frontend_bp.errorhandler(403)
def edit_forbidden(error):
    return render_template('403.html'), 403


# autocomplete handler
@frontend_bp.route('/api/autocomplete')
def autocomplete():
    query = request.args.get('query')
    chunk = request.args.get('chunk')
    suggestions_type = request.args.get('t')
    suggestions_per_query = app.config['SUGGESTIONS_PER_QUERY']

    if suggestions_type == 'authors':
        suggestions = get_authors_autocomplete(
            query,
            chunk,
            suggestions_per_query)
    elif suggestions_type == 'books':
        suggestions = get_books_autocomplete(
            query,
            chunk,
            suggestions_per_query)
    else:
        suggestions = None

    return jsonify(suggestions)


# user_cabinet
@frontend_bp.route('/user/cabinet')
@login_required
def user_cabinet():
    return render_template('user_cabinet.html')


# check if user can edit entity
def extended_roles_checker(entity):
    user_roles = [r.name.lower() for r in current_user.roles]
    if (
            EDITOR_ROLE or ADMIN_ROLE not in user_roles
            or entity.user_id == current_user.id
    ):
        return
    abort(403)


# deleting entities
@frontend_bp.route('/api/delete-entity', methods=['GET', 'DELETE'])
def delete_entity():
    if not current_user.is_authenticated:
        abort(403)

    entity_type = request.args.get('entityType')
    entity_id = request.args.get('id')
    if entity_type == 'author':
        entity = get_author_by_id(entity_id)
    elif entity_type == 'book':
        entity = get_book_by_id(entity_id)

    extended_roles_checker(entity)
    delete_db_entity(entity)

    return Response(status='200')

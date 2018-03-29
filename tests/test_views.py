from string import ascii_uppercase

from mock import patch, call, Mock, MagicMock
from flask_testing import TestCase
from flask import Response

from projecto import create_app


class TestViews(TestCase):
    render_templates = False

    def create_app(self):
        app = create_app(settings_module='tests.settings_test')
        return app


    def setUp(self):
        self.mocks = {
            'get_book_by_id': None,
            'get_author_by_id': None,
            'get_entities_for_letter': None,
            'get_books_count': None,
            'get_authors_count': None,
            'get_all_books_with_sections': None,
            'get_all_authors_with_sections': None,
            'get_entities_for_letter': None,
            'add_book': None,
            'add_author': None,
            'update_book': None,
            'update_author': None,
            'find_authors': None,
            'get_book_by_id': None,
            'extended_roles_checker': None,
            'delete_db_entity': None,
            'Pagination': None,
            'AddBookForm': None,
            'AddAuthorForm': None,
            'AuthorsSearchForm': None,
            'EditAuthorForm': None,
            'current_user': None,
            'get_authors_autocomplete': None,
            'get_books_autocomplete': None
        }

        for i in self.mocks.keys():
            patcher = patch('projecto.frontend.views.{}'.format(i))
            self.mocks[i] = patcher.start()
            self.addCleanup(patcher.stop)


    def test_index_returns_templates_and_json(self):
        self.client.get('/')
        self.assert_template_used('index.html')


    def test_about_returns_template(self):
        self.client.get('/about')
        self.assert_template_used('about.html')


    def test_links_return_template(self):
        self.client.get('/links')
        self.assert_template_used('links.html')


    def test_book_view_return_templates(self):
        self.client.get('/books')
        self.assert_template_used('books.html')

    def test_show_book_by_id_returns_template_and_has_proper_context(self):
        self.mocks['get_book_by_id'].return_value = 0
        self.client.get('/books/show/1')
        self.assert_template_used('show_book.html')
        self.assert_context('book_id', 1)


    def test_show_all_books_returns_template_and_has_proper_context(self):
        self.mocks['get_books_count'].return_value = (
            self.app.config['MAX_ENTITIES_PER_CORPUS_PAGE'])
        self.mocks['get_all_books_with_sections'].return_value = [1,2,3]
        self.client.get('/books/show-all')
        self.assert_template_used('b_corpus.html')
        self.assert_context('books', [1,2,3])
        self.assert_context('lettering', False)
        self.assert_context('ascii_letters', ascii_uppercase)


    def test_show_all_books_per_letter_returns_template_and_has_proper_context(self):
        self.mocks['get_entities_for_letter'].return_value = ['book1', 'book2']
        self.client.get('/books/show-all/A')
        self.assert_template_used('b_corpus.html')
        self.assert_context('books', ['book1', 'book2'])
        self.assert_context('lettering', True)
        self.assert_context('ascii_letters', ascii_uppercase)


    def tets_add_books_returns_template(self):
        self.mocks['add_book'].return_value = 'added'
        r = self.client.post('/books/add')
        self.mocks['add_book']\
            .assert_called_once()
        self.assert_redirects(r, '/books')
        self.client.get('/books/add')
        self.assert_template_used('add_book.html')


    def test_edit_book_returns_template_and_has_proper_context(self):
        self.mocks['get_book_by_id'].return_value = Mock(authors=[])
        self.client.get('books/edit/1')
        self.assert_template_used('edit_book.html')
        self.assert_context('book', self.mocks['get_book_by_id']())
        self.assert_context('book_id', 1)
        self.assert_context('authors_array', [])

        self.mocks['update_book'].return_value = 'updated'
        r = self.client.post('books/edit/1')
        self.assert_redirects(r, '/books')


    def test_author_view_return_templates_returns_template_and_has_proper_context(self):
        self.client.get('/authors')
        self.assert_template_used('authors.html')
        self.assert_context('form', self.mocks['AuthorsSearchForm']())
        self.assert_context('pagination', None)
        self.mocks['find_authors'].return_value = []
        self.client.get('/authors/2?&per_page=40')
        self.mocks['Pagination']\
            .assert_called_once_with(None, None, None, None, None)


    def test_show_all_authors_returns_template_and_has_proper_context(self):
        self.mocks['get_authors_count'].return_value = (
            self.app.config['MAX_ENTITIES_PER_CORPUS_PAGE'])
        self.mocks['get_all_authors_with_sections'].return_value = [3, 2, 1]
        self.client.get('/authors/show-all')
        self.assert_template_used('corpus.html')
        self.assert_context('authors', [3, 2, 1])
        self.assert_context('lettering', False)
        self.assert_context('ascii_letters', ascii_uppercase)


    def test_show_all_books_per_letter_returns_template_and_has_proper_context(self):
        self.mocks['get_entities_for_letter']\
            .return_value = ['author1', 'author2']
        self.client.get('/authors/show-all/A')
        self.assert_template_used('corpus.html')
        self.assert_context('authors', ['author1', 'author2'])
        self.assert_context('lettering', True)
        self.assert_context('ascii_letters', ascii_uppercase)


    def test_add_authors_returns_template_and_redirects(self):
        self.mocks['add_author'].return_value = 'added'
        r = self.client.post('/authors/add')
        self.mocks['add_author']\
            .assert_called_once()
        self.assert_redirects(r, '/authors')


    def test_edit_author_returns_template_and_has_proper_context_and_redirects(self):
        self.mocks['get_author_by_id'].return_value = MagicMock(books=[])
        self.client.get('authors/edit/1')
        self.assert_template_used('edit_author.html')
        self.assert_context('author', self.mocks['get_author_by_id']())
        self.assert_context('author_id', 1)
        self.assert_context('books_array', [])

        self.mocks['update_author'].return_value = 'updated'
        r = self.client.post('authors/edit/1')
        self.assert_redirects(r, '/authors')


    def test_delete_entity_authors_makes_correct_calls(self):
        self.mocks['current_user'].is_authenticated = True
        entity_mock = MagicMock(name='lel', surname='lol')
        self.mocks['get_author_by_id'].return_value = entity_mock
        r = self.client.delete('/api/authors/1')
        self.mocks['get_author_by_id'].assert_called_once_with(1)
        self.mocks['extended_roles_checker']\
            .assert_called_once_with(entity_mock)
        self.mocks['delete_db_entity'].assert_called_once_with(entity_mock)
        self.assert_status(r, 200)


    def test_delete_entity_books_makes_correct_calls(self):
        self.mocks['current_user'].is_authenticated = True
        entity_mock = MagicMock(title='kekbook')
        self.mocks['get_book_by_id'].return_value = entity_mock
        r = self.client.delete('/api/books/12')
        self.mocks['get_book_by_id'].assert_called_once_with(12)
        self.mocks['extended_roles_checker']\
            .assert_called_once_with(entity_mock)
        self.mocks['delete_db_entity'].assert_called_once_with(entity_mock)
        self.assert_status(r, 200)


    def test_autocomplete_returns_suggestions(self):
        self.mocks['get_authors_autocomplete'].return_value = 777
        r = self.client.get('/api/autocomplete?query=l&chunk=1&t=authors')
        self.mocks['get_authors_autocomplete']\
            .assert_called_once_with(
                'l', '1', self.app.config['SUGGESTIONS_PER_QUERY'])
        self.assertIsInstance(r, Response)
        self.assertEqual(r.data, '777\n')


    def test_get_authors_books_returns_items(self):
        self.mocks['get_entities_for_letter'].return_value = 'items'
        r = self.client.get('/api/authors?letter=k&chunk=8')
        self.mocks['get_entities_for_letter']\
            .assert_called_with(
                'authors',
                self.app.config['MAX_ENTITIES_PER_CORPUS_PAGE'],
                'k',
                '8'
            )
        self.assertEqual(r.data, '"items"\n')

        self.mocks['get_entities_for_letter'].return_value = 'items2'
        r = self.client.get('/api/books?letter=g&chunk=2')
        self.mocks['get_entities_for_letter']\
            .assert_called_with(
                'books',
                self.app.config['MAX_ENTITIES_PER_CORPUS_PAGE'],
                'g',
                '2'
            )
        self.assertEqual(r.data, '"items2"\n')


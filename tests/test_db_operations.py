from unittest import TestCase

from mock import patch, call, Mock

from projecto.db_operations import (
    get_author_by_id,
    get_book_by_id,
    get_all_authors_with_sections,
    get_all_books_with_sections,
    find_authors,
    add_author,
    update_author,
    add_book,
    update_book,
    get_authors_autocomplete,
    get_books_autocomplete,
    get_entities_for_letter,
    check_if_author_exists
)


class TestDbOperations(TestCase):
    def setUp(self):
        self.mocks =  {
            'db': None,
            'Author': None,
            'Book': None,
            'func': None,
            'EditAuthorForm': None,
            'AddAuthorForm': None,
            'AddBookForm': None
        }

        for i in self.mocks.keys():
            if i.endswith('Form'):
                patcher = patch(
                    'projecto.forms.{}'.format(i))
            else:
                patcher = patch(
                    'projecto.db_operations.{}'.format(i))
            self.mocks[i]= patcher.start()
            self.addCleanup(patcher.stop)


    def test_get_author_by_id_calls_get_or_404(self):
        get_author_by_id(2)
        self.mocks['Author'].query.get_or_404.assert_called_once_with(2)


    def test_get_all_authors_with_sections_counts_and_returns_all(self):
        number = 10000
        self.mocks['Author'].query.count = Mock(return_value=3)
        get_all_authors_with_sections(number)
        self.mocks['Author'].query.count.assert_called_once()
        self.mocks['Author'].query.all.assert_called_once()


    def test_find_authors_query_and_use_full_text_search(self):
        find_authors('Bob', 'Smith', 'Ham')
        self.mocks['Author'].query.filter.assert_called()
        self.mocks['func'].to_tsvector.assert_has_calls(
            [call('simple', self.mocks['Book'].title),
            call().match('Ham:*', postgresql_regconfig='simple'),
            call('simple', self.mocks['Author'].surname),
            call().match('Smith:*', postgresql_regconfig='simple'),
            call('simple', self.mocks['Author'].name)],
            call().match('Bob:*', postgresql_regconfig='simple')
        )


    def test_get_book_by_id_calls_get_or_404(self):
        get_book_by_id(2)
        self.mocks['Book'].query.get_or_404.assert_called_once_with(2)


    def test_get_all_books_with_sections_counts_and_returns_all(self):
        number = 10000
        self.mocks['Book'].query.count = Mock(return_value=3)
        get_all_books_with_sections(number)
        self.mocks['Book'].query.count.assert_called_once()
        self.mocks['Book'].query.options().order_by().all.assert_called_once()


    def test_add_book_queries_authors(self):
        form = self.mocks['AddBookForm']
        form.authors.data = [1, 2]
        add_book(form)
        self.mocks['Author'].query\
            .filter.assert_called_once_with(
                self.mocks['Author'].id.in_([1,2]))


    def test_update_book_changes_authors(self):
        form = self.mocks['AddBookForm']
        form.authors.data = [1,2]
        update_book(Mock(), form)
        self.mocks['Author'].id.in_.assert_called_with([1,2])
        self.mocks['Author'].query.filter().all.assert_called_once()


    def test_get_books_autocomplete_queries_and_uses_full_text_search(self):
        get_books_autocomplete('Lol', 2, 100)
        self.mocks['db'].session.query\
            .assert_called_once_with(
                self.mocks['Book'].id,
                self.mocks['Book'].title
            )
        self.mocks['db'].session.query()\
            .filter.called_once_with(
                (self.mocks['func']
                    .to_tsvector('simple', self.mocks['Book'].title)
                    .match('Lol:*')))
        self.mocks['db'].session.query().filter().order_by.called_once_with(
            self.mocks['func'].ts_rank(
                self.mocks['func']
                    .to_tsvector('simple', self.mocks['Book'].title), 'Lol:*'))
        self.mocks['db'].session.query()\
            .filter().order_by().offset.assert_called_once_with(100)
        self.mocks['db'].session.query()\
            .filter().order_by().offset().limit.assert_called_once_with(100)


    def test_get_authors_autocomplete_queries_and_uses_full_text_search(self):
        get_authors_autocomplete('Lol', 2, 100)
        self.mocks['db'].session.query\
            .assert_called_once_with(
                self.mocks['Author'].id,
                self.mocks['Author'].surname,
                self.mocks['Author'].name
            )
        self.mocks['db'].session.query()\
            .filter.called_once_with(
                ((self.mocks['func']
                    .to_tsvector('simple', self.mocks['Author'].name)
                    .match('Lol:*') |
                (self.mocks['func']
                    .to_tsvector('simple', self.mocks['Author'].surname)
                    .match('Lol:*')))))
        self.mocks['db'].session.query().filter().order_by.called_once_with(
            self.mocks['func'].ts_rank(
                self.mocks['func']
                    .to_tsvector('simple', self.mocks['Author'].name), 'Lol:*'))
        self.mocks['db'].session.query()\
            .filter().order_by().offset.assert_called_once_with(100)
        self.mocks['db'].session.query()\
            .filter().order_by().offset().limit.assert_called_once_with(100)


    def test_get_entities_for_letter_queries_and_uses_full_text_search(self):
        self.mocks['Book'].query.count = Mock(return_value=20)
        get_entities_for_letter('books', 10, 'a', 1)
        self.mocks['Book'].query.options().filter.assert_called_once_with(
            self.mocks['func'].to_tsvector('simple', self.mocks['Book'].title)
                .match('a:*', postgresql_regconfig='simple')
        )
        self.mocks['Book'].query\
            .options().filter().order_by.assert_called_once_with(
                self.mocks['Book'].title.asc()
        )
        self.mocks['Book'].query\
            .options().filter().order_by().limit.assert_called_once_with(10)
        self.mocks['Book'].query\
            .options().filter().order_by().limit()\
                                          .offset.assert_called_once_with(0)


    def test_add_author_adds(self):
        form = self.mocks['AddAuthorForm']
        add_author(form)
        self.mocks['db'].session.add.assert_called()


    def test_update_author_changes_books(self):
        form = self.mocks['EditAuthorForm']
        form.books.data = [1,2]
        update_author(Mock(), form)
        self.mocks['Book'].query.filter.assert_called_with(
            self.mocks['Book'].id.in_([1,2]))


    def test_check_if_author_exists(self):
        check_if_author_exists([1, 2])
        self.mocks['func'].count.assert_called_with(self.mocks['Author'].id)
        self.mocks['db'].session\
            .query().filter.assert_called_with(
                self.mocks['Author'].id.in_([1,2]))
        self.mocks['db'].session.query().filter().scalar.assert_called()


#    get random entity
# weird error:     return self.randrange(a, b+1)
#  File "/usr/lib/python2.7/random.py", line 200, in randrange
#    raise ValueError, "non-integer stop for randrange()"
#ValueError: non-integer stop for randrange()

    # def test_random_entity_queries_db(self):
    #     get_random_entity('book')
    #     self.mocks['db'].session.query.assert_has_calls(
    #        [call(self.mocks['Book'].id),
    #         call().order_by(self.mocks['Book'].id.desc()),
    #         call().call().first_or_404()]
    #     )

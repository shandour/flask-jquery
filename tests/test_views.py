from mock import patch, call, Mock
from flask_testing import TestCase
from flask import Response

#from projecto.frontend.views import *
from projecto import create_app


class TestViews(TestCase):
    render_templates = False

    def create_app(self):
        app = create_app(settings_module='tests.settings_test')
        #app.config['LIVESERVER_PORT'] = 0

        return app


    # def setUp(self):
    #     self.mocks = {
    #         'get_book_by_id': None,
    #         'get_entities_for_letter': None,
    #         'AddBookForm': None
    #     }

    #     for i in self.mocks.keys():
    #         patcher = patch('projecto.frontend.views.{}'.format(i))
    #         self.mocks[i] = patcher.start()
    #         self.addCleanup(patcher.stop)


    def test_views_return_templates_and_json(self):
        self.client.get('/')
        self.assert_template_used('index.html')

        # self.client.get('/about')
        # self.assert_template_used('about.html')

        # self.client.get('/links')
        # self.assert_template_used('links.html')

        # self.client.get('/books')
        # self.assert_template_used('books.html')

        # self.mocks['get_book_by_id'].return_value = 0
        # self.client.get('/books/show/1')
        # self.assert_template_used('show_book.html')

        # self.mocks['get_entities_for_letter'].return_value = 0
        # r = self.client.get('/api/get-entities')
        # self.assertIsInstance(r, Response)
        # self.assertEqual(r.data, '0\n')

    def test_lol(self):
        self.client.get('/')
        self.assert_template_used('index.html')





from http import HTTPStatus

from django.test import Client, TestCase


class StaticURLTests(TestCase):
    def setUp(self):

        self.guest_client = Client()

    def test_author_page(self):

        urls = [
            '/about/author/',
            '/about/tech/'
        ]
        for adress in urls:
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)

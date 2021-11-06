from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post


User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            text='Текст',
            author=User.objects.create_user(username='SeyMyName'),
        )
        Group.objects.create(
            slug='slug_test',
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='NoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_guest(self):
        """Тестируем страницы для гостевого пользователя"""
        pages = [
            '/',
            '/group/slug_test/',
            '/profile/SeyMyName/',
            f'/posts/{self.post.pk}/',
        ]
        for adress in pages:
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_authorized(self):
        """Тестируем страницы для авторизованного пользователя"""
        authorized_pages = [
            '/create/',
            f'/posts/{self.post.pk}/edit/',
        ]
        for page in authorized_pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/slug_test/': 'posts/group_list.html',
            '/profile/SeyMyName/': 'posts/profile.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

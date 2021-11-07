from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache

from posts.models import Group, Post

User = get_user_model()


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Название',
            slug='slug_test',
            description='Описание',
        )
        cls.post = Post.objects.create(
            text='Текст',
            author=User.objects.create_user(username='SayNyName'),
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='AntonBek')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache_index_page(self):
        """Проверка работоспособности кэш."""
        response = self.authorized_client.get(reverse('posts:index'))
        cache_save = response.content
        self.post.delete()
        response = self.authorized_client.get(reverse('posts:index'))
        cache_after_del = response.content
        self.assertEqual(cache_after_del, cache_save)
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        cache_afte_clear = response.content
        self.assertNotEqual(cache_afte_clear, cache_save)

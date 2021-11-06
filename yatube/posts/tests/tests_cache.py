from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

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
        first_object = response.context['page_obj'][0]
        self.post.delete()
        post_pub_date_0 = first_object.pub_date
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        post_image = first_object.image

        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_pub_date_0, self.post.pub_date)
        self.assertEqual(post_author_0, self.post.author)
        self.assertEqual(post_group_0, self.post.group)
        self.assertEqual(post_image, self.post.image)

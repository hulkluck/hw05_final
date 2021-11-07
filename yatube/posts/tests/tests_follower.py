from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, Follow


User = get_user_model()


class FollowerTests(TestCase):
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
            author=User.objects.create_user(username='Following'),
            group=cls.group,
        )
        cls.follow = Follow.objects.create(
            user=User.objects.create_user(username='Follower'),
            author=cls.post.author
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='AuthUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_following_auth_user(self):
        """
        Проверка подписки на авторов
        """
        follow_count = Follow.objects.count()
        data_form = {
            'user': self.user,
            'author': self.post.author,
        }
        response = self.authorized_client.post(
            reverse('posts:profile_follow', args={self.post.author}),
            data=data_form
        )
        self.assertRedirects(response, reverse(
            'posts:profile', args={self.post.author}), HTTPStatus.FOUND)
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        self.assertTrue(
            Follow.objects.filter(
                user=self.user,
                author=self.post.author,
            ).exists()
        )

    def test_unfollowing_auth_user(self):
        """
        Проверка отписки от авторов
        """
        follow_count = Follow.objects.count()
        data_form = {
            'user': self.follow.user,
            'author': self.post.author,
        }
        response = self.authorized_client.post(
            reverse('posts:profile_unfollow', args={self.post.author}),
            data=data_form
        )
        self.assertRedirects(response, reverse(
            'posts:profile', args={self.post.author}), HTTPStatus.FOUND)
        self.assertEqual(Follow.objects.count(), follow_count)

    def test_follow_page_correct_contex_auth_user(self):
        """
        Проверка страницы follow на отображение правильного контекста
        """
        Follow.objects.create(user=self.user, author=self.post.author)
        response = self.authorized_client.get(
            reverse('posts:follow_index'))
        first_object = response.context['page_obj'][0]
        post_author = first_object.author
        post_text = first_object.text
        self.assertEqual(post_text, self.post.text)
        self.assertEqual(post_author, self.post.author)

    def test_follow_page_correct_contex_next_user(self):
        """
        Проверка страницы follow на отображение правильного контекста
        с другим юзером
        """
        next = Post.objects.create(
            text='Текст_2',
            author=self.follow.user,
        )
        Follow.objects.create(user=self.user, author=self.post.author)
        response = self.authorized_client.get(
            reverse('posts:follow_index'))
        first_object = response.context['page_obj'][0]
        post_author = first_object.author
        post_text = first_object.text
        self.assertNotEqual(post_text, next.text)
        self.assertNotEqual(post_author, next.author)

    def test_auth_follow_auth(self):
        """
        Проверка запрета подписки на себя любимого
        """
        follow_count = Follow.objects.count()
        response = self.authorized_client.post(
            reverse('posts:profile_follow', args={self.user}))
        self.assertRedirects(response, reverse(
            'posts:profile', args={self.user}))
        self.assertEqual(Follow.objects.count(), follow_count)

    def test_auth_follow_re(self):
        """
        Проверка запрета повторной подписки
        """
        Follow.objects.create(user=self.user, author=self.post.author)
        follow_count = Follow.objects.count()
        response = self.authorized_client.post(
            reverse('posts:profile_follow', args={self.post.author}))
        self.assertRedirects(response, reverse(
            'posts:profile', args={self.post.author}), HTTPStatus.FOUND)
        self.assertEqual(Follow.objects.count(), follow_count)

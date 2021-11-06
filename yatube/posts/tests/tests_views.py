from http import HTTPStatus
from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from yatube.settings import POSTS_PER_PAGE, POSTS_PER_PAGE_TEST

from posts.models import Group, Post, Comment, Follow


User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Название',
            slug='slug_test',
            description='Описание',
        )
        cls.group_two = Group.objects.create(
            title='Название2',
            slug='slug_test_two',
            description='Описание2',
        )
        cls.post = Post.objects.create(
            text='Текст',
            author=cls.follow.user,
            group=cls.group,
        )
        cls.post_two = Post.objects.create(
            text='Текст2',
            group=cls.group_two,
            author=User.objects.create_user(username='SeyMyName'),
        )
        cls.comment = Comment.objects.create(
            text='Мой первый комментарий',
            author=User.objects.create_user(username='CommentMan'),
            post=cls.post
        )
        cls.follow = Follow.objects.create(
            user=User.objects.create_user(username='Follower'),
            author=cls.post_two.author
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = self.follow.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_uses_correct_template(self):
        """URL-адреса используют соответствующие шаблоны."""
        tamplates_page = {
            reverse('posts:post_edit', args={self.post.pk}):
            'posts/create_post.html',
            reverse('posts:post_detail', args={self.post.pk}):
            'posts/post_detail.html',
            reverse('posts:post_create'):
            'posts/create_post.html',
            reverse('posts:profile', args={'SeyMyName'}):
            'posts/profile.html',
            reverse('posts:group_list', kwargs={'slug': 'slug_test'}):
            'posts/group_list.html',
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:follow_index'): 'posts/follow.html'
        }
        for reverse_name, template in tamplates_page.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def assert_equal_method(self, pub_date, text, author, group, image):
        self.assertEqual(text, self.post.text)
        self.assertEqual(pub_date, self.post.pub_date)
        self.assertEqual(author, self.post.author)
        self.assertEqual(group, self.post.group)
        self.assertEqual(image, self.post.image)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильны контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][1]
        post_pub_date_0 = first_object.pub_date
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        post_image = first_object.image
        return self.assert_equal_method(
            post_pub_date_0, post_text_0, post_author_0,
            post_group_0, post_image)

    def test_post_detail_page_show_correct_context(self):
        """
        Шаблон post_detail сформирован с правильны
        контекстом и комментарем.
        """
        response = (self.authorized_client.
                    get(reverse('posts:post_detail', args={self.post.pk})))
        self.assertEqual(response.context.get('post').text, self.post.text)
        self.assertEqual(response.context.get('post').author, self.post.author)
        self.assertEqual(response.context.get('post').group, self.post.group)
        self.assertEqual(response.context.get(
            'post').pub_date, self.post.pub_date)
        self.assertEqual(response.context['comments'][0], self.comment)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильны контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'slug_test'}))
        first_object = response.context['page_obj'][0]
        post_pub_date_0 = first_object.pub_date
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        post_image = first_object.image
        return self.assert_equal_method(
            post_pub_date_0, post_text_0, post_author_0,
            post_group_0, post_image)

    def test_profrle_page_show_correct_context(self):
        """Шаблон profrle сформирован с правильны контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', args={'Follower'}))
        first_object = response.context['page_obj'][0]
        post_pub_date_0 = first_object.pub_date
        post_text_0 = first_object.text
        post_group_0 = first_object.group
        post_author_0 = first_object.author
        post_image = first_object.image
        return self.assert_equal_method(
            post_pub_date_0, post_text_0, post_author_0,
            post_group_0, post_image)

    def test_create_page_show_correct_context(self):
        """Типы полей форм create/edit соответствуют ожиданиям"""
        reverse_urls = [
            reverse('posts:post_create'),
            reverse('posts:post_edit', args={self.post.pk}),
        ]
        for urls in reverse_urls:
            response = self.authorized_client.get(urls)
            form_fields = {
                'text': forms.fields.CharField,
                'group': forms.fields.ChoiceField,
            }
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_reverse = response.context['form'].fields[value]
                    self.assertIsInstance(form_reverse, expected)

    def test_group_list_two_not_in_context(self):
        """Проверка на осутствие поста в другой группе."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'slug_test_two'}))
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author
        post_text_0 = first_object.text
        post_group_0 = first_object.group

        self.assertNotEqual(post_text_0, self.post.text)
        self.assertNotEqual(post_author_0, self.post.author)
        self.assertNotEqual(post_group_0, self.post.group)

    def test_following_auth_user(self):
        """
        Проверка подписки на авторов
        """
        follow_count = Follow.objects.count()
        Follow.objects.create(user=self.user, author=self.post.author)
        self.assertEqual(Follow.objects.count(), follow_count + 1)

    def test_unfollowing_auth_user(self):
        """
        Проверка отписки от авторов
        """
        follow_count = Follow.objects.count()
        Follow.objects.filter(user=self.follow.user,
                              author=self.follow.author).delete()
        self.assertEqual(Follow.objects.count(), follow_count - 1)

    def test_follow_page_correct_contex_auth_user(self):
        """
        Проверка страницы follow на отображение правильного контекста
        """
        response = self.authorized_client.get(
            reverse('posts:follow_index'))
        first_object = response.context['page_obj'][0]
        post_author = first_object.author
        post_text = first_object.text
        self.assertEqual(post_text, self.post_two.text)
        self.assertEqual(post_author, self.post_two.author)

    def test_follow_page_correct_contex_next_user(self):
        """
        Проверка страницы follow на отображение правильного кконтекста
        с другим юзером
        """
        response = self.authorized_client.get(
            reverse('posts:follow_index'))
        first_object = response.context['page_obj'][0]
        post_author = first_object.author
        post_text = first_object.text
        self.assertNotEqual(post_text, self.post.text)
        self.assertNotEqual(post_author, self.post.author)

    def test_auth_follow_auth(self):
        """
        Проверка запрета подписки на себя любимого
        """
        follow_count = Follow.objects.count()
        response = self.authorized_client.post(
            reverse('posts:profile_follow', args={self.post.author}))
        self.assertRedirects(response, reverse(
            'posts:profile', args={self.post.author}))
        self.assertEqual(Follow.objects.count(), follow_count)

    def test_auth_follow_re(self):
        follow_count = Follow.objects.count()
        response = self.authorized_client.post(
            reverse('posts:profile_follow', args={self.post_two.author}))
        self.assertRedirects(response, reverse(
            'posts:profile', args={self.post_two.author}), HTTPStatus.FOUND)
        self.assertEqual(Follow.objects.count(), follow_count)


class PaginatorViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug='test_slug'
        )
        objs = [Post(author=cls.user, text='Тестовый пост',
                     group=cls.group) for i in range(13)]
        Post.objects.bulk_create(objs)
        cls.guest_client = Client()
        cls.pages_uses_paginator = [
            reverse('posts:index'),
            reverse('posts:profile', kwargs={'username': 'test_user'}),
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}),
        ]

    def test_first_page_contains_ten_records(self):
        """Проверка первой страницы пагинатора"""
        for reverse_page in self.pages_uses_paginator:
            with self.subTest(reverse_page=reverse_page):
                response = self.client.get(reverse_page)
                self.assertEqual(
                    len(response.context['page_obj']), POSTS_PER_PAGE)

    def test_second_page_contains_three_records(self):
        """Проверка второй страницы пагинатора"""
        for reverse_page in self.pages_uses_paginator:
            with self.subTest(reverse_page=reverse_page):
                response = self.client.get(reverse_page + '?page=2')
                self.assertEqual(
                    len(response.context['page_obj']), POSTS_PER_PAGE_TEST)

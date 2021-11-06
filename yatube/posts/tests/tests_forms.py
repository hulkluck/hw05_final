import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls.base import reverse

from posts.forms import PostForm
from posts.models import Post


User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)



@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=User.objects.create_user(username='SeyMyName'),
        )

        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.user = self.post.author
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Проверка создания поста"""
        post_count = Post.objects.count()
        post_image = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='mupic.jpg',
            content=post_image,
            content_type='image/gif',
        )
        form_data = {
            'text': 'текст',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', args={self.post.author}), HTTPStatus.FOUND)
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
            ).exists()
        )

    def test_edit_post(self):
        """Проверка редактирования поста"""
        post_count = Post.objects.count()
        form_data = {
            'text': 'текст_два',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args={self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', args={self.post.pk}), HTTPStatus.FOUND)
        self.assertEqual(Post.objects.count(), post_count)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
            ).exists()
        )

    def test_guest_client_create_post(self):
        """Проверка на редирект при попытке создания
        поста не авторизованным юзером
        """
        post_count = Post.objects.count()
        response = self.guest_client.post(
            reverse('posts:post_create'))
        path_redirect = reverse('users:login')
        path_create = reverse('posts:post_create')
        self.assertRedirects(response,
                             f'{path_redirect}?next={path_create}',
                             HTTPStatus.FOUND)
        self.assertEqual(Post.objects.count(), post_count)

    def test_guest_client_comment_to_post(self):
        """Проверка на запрет
        комментирования постов для гостя
        """
        response = self.guest_client.post(reverse('posts:add_comment', args={self.post.pk}))
        path_redirect = reverse('users:login')
        path_comment = reverse('posts:add_comment', args={self.post.pk})
        self.assertRedirects(response,
                             f'{path_redirect}?next={path_comment}',
                             HTTPStatus.FOUND)

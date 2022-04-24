import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.test import override_settings
from django.urls import reverse

from ..models import Group, Post


User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NewUser')
        cls.group_1 = Group.objects.create(
            title='Тестовая группа 1',
            slug='test_cats',
            description='Тестовое описание 1',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_dogs',
            description='Тестовое описание 2',
        )
        cls.post = Post.objects.create(
            text='Текст первого поста',
            author=cls.user,
            group=cls.group_1,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.auth_user = Client()
        self.auth_user.force_login(self.user)

    def test_post_create_form(self):
        """Форма создаёт запись post."""
        posts_count = Post.objects.count()
        small_gif = (            
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif',
        )
        form_data = {
            'text': 'Текст поста, который больше 15 символов',
            'group': self.group_1.pk,
            'image': uploaded,
        }
        response = self.auth_user.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        sorted_posts = Post.objects.order_by('-id')
        new_post = sorted_posts[0]
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.user.username}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(new_post.text, form_data['text'])
        self.assertEqual(new_post.group.pk, form_data['group'])
        self.assertEqual(new_post.author, self.user)
        self.assertEqual(new_post.image, 'posts/small.gif')

    def test_post_edit_form(self):
        """Пост корректно отредактирован с помощью формы."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст первого поста (отредактирован)',
            'group': self.group_2.pk,
        }
        response = self.auth_user.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True,
        )
        edited_post = Post.objects.get(pk=self.post.pk)
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(edited_post.text, form_data['text'])
        self.assertEqual(edited_post.group.pk, form_data['group'])

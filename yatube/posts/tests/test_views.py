import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.test import override_settings
from django.urls import reverse

from yatube.settings import POSTS_PER_PAGE
from ..models import Comment, Follow, Group, Post


User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


def compare_two_posts(self, post1, post2):
    self.assertEqual(post1.text, post2.text)
    self.assertEqual(post1.author, post2.author)
    self.assertEqual(post1.group, post2.group)
    self.assertEqual(post1.image, post2.image)


class PostsTemplatesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NewUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_cats',
            description='Описание группы',
        )
        cls.post = Post.objects.create(
            text='Новый пост, в котором точно больше 15 символов',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)

    def test_pages_use_correct_templates(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            ): 'posts/create_post.html',
        }
        for reverse_name, template in templates_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_user.get(reverse_name)
                self.assertTemplateUsed(response, template)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsContextTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
        cls.user_1 = User.objects.create_user(username='User_1')
        cls.user_2 = User.objects.create_user(username='User_2')
        cls.group_1 = Group.objects.create(
            title='Тестовая группа 1',
            slug='test_cats',
            description='Описание группы 1',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_dogs',
            description='Описание группы 2',
        )
        for post_number in range(10):
            if post_number < 5:
                Post.objects.create(
                    text=f'Текст поста {9-post_number}',
                    author=cls.user_2,
                    group=cls.group_2,
                    image=uploaded,
                )
            else:
                Post.objects.create(
                    text=f'Текст поста {9-post_number}',
                    author=cls.user_1,
                    group=cls.group_1,
                    image=uploaded,
                )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.auth_user_1 = Client()
        self.auth_user_1.force_login(self.user_1)
        self.auth_user_2 = Client()
        self.auth_user_2.force_login(self.user_2)

    def test_page_index_show_correct_context(self):
        """Шаблон страницы index сформирован с правильным контекстом."""
        response = self.client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        post_id_0 = first_object.pk
        post_image_0 = first_object.image
        self.assertEqual(post_id_0, first_object.id)
        self.assertEqual(post_text_0, Post.objects.get(pk=post_id_0).text)
        self.assertEqual(post_author_0, self.user_1)
        self.assertEqual(post_group_0, self.group_1)
        self.assertEqual(post_image_0, Post.objects.get(pk=post_id_0).image)

    def test_page_group_list_show_correct_context(self):
        """Шаблоны страниц group_list сформированы с правильным контекстом."""
        groups = {
            reverse(
                'posts:group_list', kwargs={'slug': 'test_cats'}
            ): self.group_1,
            reverse(
                'posts:group_list', kwargs={'slug': 'test_dogs'}
            ): self.group_2,
        }
        for name, group in groups.items():
            with self.subTest(group=group):
                response = self.client.get(name)
                test_group = response.context['group']
                self.assertEqual(test_group.title, group.title)
                self.assertEqual(test_group.slug, group.slug)
                self.assertEqual(test_group.description, group.description)
                for post in response.context['page_obj']:
                    self.assertEqual(post.group, group)
                    self.assertTrue(post.image)

    def test_page_profile_show_correct_context(self):
        """
        Шаблоны страниц пользователей
        сформированы с правильным контекстом.
        """
        users = {
            reverse(
                'posts:profile', kwargs={'username': self.user_1.username}
            ): self.user_1,
            reverse(
                'posts:profile', kwargs={'username': self.user_2.username}
            ): self.user_2,
        }
        for name, user in users.items():
            with self.subTest(user=user):
                response = self.client.get(name)
                author = response.context['author']
                self.assertEqual(author.username, user.username)
                for post in response.context['page_obj']:
                    self.assertEqual(post.author, user)
                    self.assertTrue(post.image)

    def test_page_post_detail_show_correct_context(self):
        """
        Шаблон отображения деталей поста
        сформирован с правильным контекстом.
        """
        for post in Post.objects.all():
            with self.subTest(post=post.pk):
                response = self.auth_user_1.get(
                    reverse('posts:post_detail', kwargs={'post_id': post.pk})
                )
                context_post = response.context['post']
                compare_two_posts(self, context_post, post)

    def test_page_create_post_show_correct_context(self):
        """Шаблон создания поста сформирован с правильным контекстом."""
        response = self.auth_user_1.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_page_edit_post_show_correct_context(self):
        """Шаблон редактирования поста сформирован с правильным контекстом."""
        for testing_post in Post.objects.filter(author=self.user_2):
            with self.subTest(post=testing_post.pk):
                response = self.auth_user_2.get(
                    reverse(
                        'posts:post_edit',
                        kwargs={'post_id': testing_post.pk}
                    )
                )
                text_initial = response.context['form'].initial['text']
                group_initial = response.context['form'].initial['group']
                edit = response.context['is_edit']
                self.assertEqual(text_initial, testing_post.text)
                self.assertEqual(group_initial, testing_post.group.pk)
                self.assertEqual(edit, True)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NewUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_cats',
            description='Описание группы',
        )
        for post_number in range(15):
            Post.objects.create(
                text=f'Текст поста {post_number}',
                author=cls.user,
                group=cls.group,
            )

    def setUp(self):
        self.auth_user = Client()
        self.auth_user.force_login(self.user)

    def test_pages_contain_correct_records(self):
        """Паджинатор отображает корректное число постов на странице."""
        names = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username}),
        ]
        for name in names:
            for page in range(1, 3):
                response = self.auth_user.get(name + f'?page={page}')
                remainder = (len(Post.objects.all())
                             - POSTS_PER_PAGE * (page - 1))
                expected = (POSTS_PER_PAGE if remainder >= POSTS_PER_PAGE
                            else remainder)
                self.assertEqual(len(response.context['page_obj']), expected)


class CommentsViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NewUser')
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
        )

    def setUp(self):
        self.auth_user = Client()
        self.auth_user.force_login(self.user)

    def test_auth_users_comment_access(self):
        """Комментарий могут оставить авторизованные пользователи."""
        comments_total = Comment.objects.count()
        request = reverse(
            'posts:add_comment', kwargs={'post_id': self.post.pk})
        form_data = {
            'text': 'Текст комментария',
        }
        self.auth_user.post(
            request,
            data=form_data,
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), comments_total + 1)

    def test_users_comment_access(self):
        """Неавторизованные пользователи не оставляют комментарий."""
        comments_total = Comment.objects.count()
        request = reverse(
            'posts:add_comment', kwargs={'post_id': self.post.pk})
        form_data = {
            'text': 'Текст комментария',
        }
        self.client.post(
            request,
            data=form_data,
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), comments_total)

    def test_comment_exists_on_post_detail_page(self):
        """Комментарий отображается на странице поста."""
        first_comment = Comment.objects.create(
            text='Тестовый комментарий',
            author=self.user,
            post=self.post,
        )
        request = reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk})
        response = self.auth_user.get(request)
        for comment in response.context['page_obj']:
            with self.subTest(comment=comment):
                self.assertEqual(comment.post, first_comment.post)
                self.assertEqual(comment.author, first_comment.author)
                self.assertEqual(comment.text, first_comment.text)


class CacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NewUser')

    def setUp(self):
        self.auth_user = Client()
        self.auth_user.force_login(self.user)
        self.post = Post.objects.create(
            text='Текст поста',
            author=self.user,
        )

    def test_index_cache_has_correct_data(self):
        """Кэш главной страницы отображает корректные данные."""
        response_1 = self.auth_user.get(reverse('posts:index'))
        self.post.delete()
        response_2 = self.auth_user.get(reverse('posts:index'))
        self.assertEqual(response_1.content, response_2.content)


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user_1 = User.objects.create_user(username='NewUser1')
        cls.user_2 = User.objects.create_user(username='NewUser2')
        cls.post_1 = Post.objects.create(
            text='Текст поста 1',
            author=cls.user_1
        )
        cls.post_2 = Post.objects.create(
            text='Текст поста 2',
            author=cls.user_2
        )

    @classmethod
    def tearDownClass(cls):
        Post.objects.all().delete()

    def setUp(self):
        self.auth_user_1 = Client()
        self.auth_user_1.force_login(self.user_1)
        self.auth_user_2 = Client()
        self.auth_user_2.force_login(self.user_2)

    def test_user_follow(self):
        """Подписка и отписка работают корректно."""
        Follow.objects.create(
            user=self.user_1,
            author=self.user_2,
        )
        following = Follow.objects.filter(user=self.user_1, author=self.user_2)
        self.assertTrue(following.exists())
        following.delete()
        self.assertFalse(following.exists())

    def test_followings_have_correct_data(self):
        """Новая запись появляется в ленте только у подписчиков."""
        Follow.objects.create(
            user=self.user_1,
            author=self.user_2
        )
        response_1 = self.auth_user_1.get(reverse('posts:follow_index'))
        response_2 = self.auth_user_2.get(reverse('posts:follow_index'))
        following_1 = len(response_1.context['page_obj'])
        following_2 = len(response_2.context['page_obj'])
        user_2_posts = len(Post.objects.filter(author=self.user_2))
        self.assertEqual(following_1, user_2_posts)
        self.assertEqual(following_2, 0)

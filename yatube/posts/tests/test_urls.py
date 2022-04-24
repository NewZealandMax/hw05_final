from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Post, Group


User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create_user(username='NewUser')
        cls.user2 = User.objects.create_user(username='NewUser2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_cats',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user1,
            text='Тестовый пост, в котором точно больше 15 символов',
            group=cls.group
        )

    def setUp(self):
        self.authorized_client_1 = Client()
        self.authorized_client_1.force_login(self.user1)
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user2)

    def test_urls_exist_at_desired_location(self):
        """Страницы, доступные гостям и пользователям с правами."""
        responses = {
            self.client.get(f'/group/{self.group.slug}/'): HTTPStatus.OK,
            self.client.get(f'/profile/{self.user1.username}/'): HTTPStatus.OK,
            self.client.get(f'/posts/{self.post.pk}/'): HTTPStatus.OK,
            self.authorized_client_1.get('/create/'): HTTPStatus.OK,
            self.authorized_client_1.get(
                f'/posts/{self.post.pk}/edit/'): HTTPStatus.OK,
            self.authorized_client_1.get(
                '/unexisting_page/'): HTTPStatus.NOT_FOUND,
        }
        for url, expected_code in responses.items():
            with self.subTest(url=url.request):
                self.assertEqual(url.status_code, expected_code)

    def test_urls_redirect_no_access(self):
        """Страницы перенаправляют пользователей без прав."""
        responses = {
            self.client.get(
                '/create/', follow=True): ('/auth/login/?next=/create/'),
            self.client.get(
                f'/posts/{self.post.pk}/edit/', follow=True): (
                    f'/auth/login/?next=/posts/{self.post.pk}/edit/'),
            self.authorized_client_2.get(
                f'/posts/{self.post.pk}/edit/', follow=True): (
                    f'/posts/{self.post.pk}/'),
        }
        for url, result in responses.items():
            with self.subTest(url=url.request):
                self.assertRedirects(url, result)

    def test_urls_use_correct_templates(self):
        """URL-адреса используют корректные шаблоны."""
        templates_url_names = {
            ('/'): 'posts/index.html',
            (f'/group/{self.group.slug}/'): 'posts/group_list.html',
            (f'/profile/{self.user1.username}/'): 'posts/profile.html',
            (f'/posts/{self.post.pk}/'): 'posts/post_detail.html',
            ('/create/'): 'posts/create_post.html',
            (f'/posts/{self.post.pk}/edit/'): 'posts/create_post.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client_1.get(url)
                self.assertTemplateUsed(response, template)

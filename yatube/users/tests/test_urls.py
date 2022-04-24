from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase


User = get_user_model()


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='NewUser')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_exist_at_desired_location(self):
        """Страницы users доступны гостям и пользователям."""
        responses = {
            self.client.get('/auth/login/'): HTTPStatus.OK,
            self.authorized_client.get(
                '/auth/password_change/'): HTTPStatus.OK,
            self.authorized_client.get(
                '/auth/password_change/done/'): HTTPStatus.OK,
            self.authorized_client.get('/auth/logout/'): HTTPStatus.OK,
            self.client.get('/auth/password_reset/'): HTTPStatus.OK,
            self.client.get('/auth/password_reset/done/'): HTTPStatus.OK,
            self.client.get('/auth/reset/<uidb64>/<token>/'): HTTPStatus.OK,
            self.client.get('/auth/reset/done/'): HTTPStatus.OK,
        }
        for address, code in responses.items():
            with self.subTest(address=address.request):
                self.assertEqual(address.status_code, code)

    def test_urls_use_correct_templates(self):
        """Страницы users используют корректные шаблоны."""
        templates_guest = {
            ('/auth/login/'): 'users/login.html',
            ('/auth/password_reset/'): 'users/password_reset_form.html',
            ('/auth/password_reset/done/'): 'users/password_reset_done.html',
            ('/auth/reset/<uidb64>/<token>/'):
            'users/password_reset_confirm.html',
            ('/auth/reset/done/'): 'users/password_reset_complete.html',
        }
        templates_auth = {
            ('/auth/password_change/'): 'users/password_change_form.html',
            ('/auth/password_change/done/'): 'users/password_change_done.html',
            ('/auth/logout/'): 'users/logged_out.html',
        }
        for url, template in templates_guest.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertTemplateUsed(response, template)
        for url, template in templates_auth.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

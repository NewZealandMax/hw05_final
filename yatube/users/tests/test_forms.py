from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


User = get_user_model()


class TestUserSignUp(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Admin')

    def test_create_user_form(self):
        """Форма создаёт нового пользователя."""
        users_count = User.objects.count()
        form_data = {
            'first_name': 'Elon',
            'last_name': 'Musk',
            'username': 'ElonMusk',
            'email': 'elon@spacex.mars',
            'password1': 'ElonMusk2030$$$',
            'password2': 'ElonMusk2030$$$',
        }
        response = self.client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertTrue(User.objects.filter(username='ElonMusk').exists())

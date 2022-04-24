from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse


class StaticURLTests(TestCase):

    def test_static_pages_exist_at_desired_location(self):
        """Статичные страницы доступны всем."""
        responses = {
            self.client.get('/about/author/'): HTTPStatus.OK,
            self.client.get('/about/tech/'): HTTPStatus.OK,
        }
        for address, code in responses.items():
            with self.subTest(address=address.request):
                self.assertEqual(address.status_code, code)

    def test_static_urls_use_correct_templates(self):
        """Статичные страницы используют корректные шаблоны."""
        templates = {
            ('/about/author/'): 'about/author.html',
            ('/about/tech/'): 'about/tech.html',
        }
        for url, template in templates.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertTemplateUsed(response, template)


class StaticViewsTests(TestCase):

    def test_about_pages_accessible_by_name(self):
        """URL, генерируемые при помощи пространства имён about, доступны."""
        names = {
            'about:author': 'about/author.html',
            'about:tech': 'about/tech.html',
        }
        for name, template in names.items():
            with self.subTest(name=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from ..models import Post

User = get_user_model()


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.post = Post.objects.create(
            author=cls.user,
            text='test_text',
        )
        cls.index_url_name = 'posts:index'

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(CacheTests.user)

    def test_cache(self):
        templates_url_names = (
            CacheTests.index_url_name,
        )
        for address in templates_url_names:
            with self.subTest(address=address):
                response = self.authorized_client.get(reverse(address))
                content = response.content
                Post.objects.all().delete()
                response = self.authorized_client.get(reverse(address))
                content2 = response.content
                self.assertEqual(content, content2)

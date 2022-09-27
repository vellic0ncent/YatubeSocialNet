from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, Client

from ..models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')

    def test_urls_uses_correct_template(self):
        templates_urls_names = {
            '/': 'posts/index.html',
        }
        for address, template in templates_urls_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_status_codes(self):
        status_codes_urls = {
            '/': HTTPStatus.OK,
            '/unknown_page/': HTTPStatus.NOT_FOUND
        }
        for address, template in status_codes_urls.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, template)


class DynamicURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='PostAuthor')
        cls.user_reader = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='test_title',
            slug='test_slug',
            description='test_description',
        )
        cls.post = Post.objects.create(
            author=cls.user_author,
            text='test_text',
        )
        cls.group_url = f'/group/{cls.group.slug}/'
        cls.user_url = f'/profile/{cls.user_author.username}/'
        cls.post_url = f'/posts/{cls.post.pk}/'
        cls.post_edit_url = f'/posts/{cls.post.pk}/edit/'
        cls.post_create_url = '/create/'
        cls.index_follow_url = '/follow/'
        cls.add_comment_url = f'/posts/{cls.post.pk}/comment/'
        cls.follow_url = f'/profile/{cls.user_author.username}/follow/'
        cls.unfollow_url = f'/profile/{cls.user_author.username}/unfollow/'
        cls.auth_url = '/auth/login/?next='

        cls.group_tmp = 'posts/group_list.html'
        cls.user_tmp = 'posts/profile.html'
        cls.post_tmp = 'posts/post_detail.html'
        cls.post_edit_tmp = 'posts/create_post.html'
        cls.post_create_tmp = 'posts/create_post.html'
        cls.index_follow_tmp = 'posts/follow.html'

    def setUp(self):
        cache.clear()
        self.guest_client = Client()

        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(DynamicURLTests.user_author)

        self.authorized_client_reader = Client()
        self.authorized_client_reader.force_login(DynamicURLTests.user_reader)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names_free_access = {
            DynamicURLTests.group_url: DynamicURLTests.group_tmp,
            DynamicURLTests.user_url: DynamicURLTests.user_tmp,
            DynamicURLTests.post_url: DynamicURLTests.post_tmp,
            DynamicURLTests.post_edit_url: DynamicURLTests.post_edit_tmp,
            DynamicURLTests.post_create_url: DynamicURLTests.post_create_tmp,
            DynamicURLTests.index_follow_url: DynamicURLTests.index_follow_tmp,
        }
        for address, template in templates_url_names_free_access.items():
            with self.subTest(address=address):
                response = self.authorized_client_author.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_redirect_anonymous(self):
        """Перенаправление анонимного пользователя по URL-адресу."""
        templates_url_names_with_redirect = {
            DynamicURLTests.post_edit_url: (
                f'{DynamicURLTests.auth_url}{DynamicURLTests.post_edit_url}'
            ),
            DynamicURLTests.post_create_url: (
                f'{DynamicURLTests.auth_url}{DynamicURLTests.post_create_url}'
            ),
            DynamicURLTests.add_comment_url: (
                f'{DynamicURLTests.auth_url}{DynamicURLTests.add_comment_url}'
            ),
            DynamicURLTests.index_follow_url: (
                f'{DynamicURLTests.auth_url}{DynamicURLTests.index_follow_url}'
            ),
            DynamicURLTests.follow_url: (
                f'{DynamicURLTests.auth_url}{DynamicURLTests.follow_url}'
            ),
            DynamicURLTests.unfollow_url: (
                f'{DynamicURLTests.auth_url}{DynamicURLTests.unfollow_url}'
            ),
        }
        for address, template in templates_url_names_with_redirect.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertRedirects(response, template)

    def test_urls_with_limited_access(self):
        """URL-адреса с ограничением прав доступа."""
        templates_urls_with_limited_access = {
            DynamicURLTests.post_edit_url: DynamicURLTests.post_url,
        }
        for address, template in templates_urls_with_limited_access.items():
            with self.subTest(address=address):
                response = self.authorized_client_reader.get(
                    address,
                    follow=True
                )
                self.assertRedirects(response, template)

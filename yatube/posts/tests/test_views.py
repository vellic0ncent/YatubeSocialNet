from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group, Follow

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='test_title',
            slug='test_slug',
            description='test_description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='test_text',
        )
        cls.index_tmp = 'posts/index.html'
        cls.group_tmp = 'posts/group_list.html'
        cls.user_tmp = 'posts/profile.html'
        cls.post_tmp = 'posts/post_detail.html'
        cls.post_edit_tmp = 'posts/create_post.html'
        cls.post_create_tmp = 'posts/create_post.html'

        cls.index_url_name = 'posts:index'
        cls.group_url_name = 'posts:group_list'
        cls.user_url_name = 'posts:profile'
        cls.post_url_name = 'posts:post_detail'
        cls.post_edit_url_name = 'posts:post_edit'
        cls.post_create_url_name = 'posts:post_create'

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostPagesTests.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse(PostPagesTests.index_url_name): PostPagesTests.index_tmp,
            reverse(PostPagesTests.group_url_name,
                    kwargs={'slug': PostPagesTests.group.slug}
                    ): PostPagesTests.group_tmp,
            reverse(PostPagesTests.user_url_name,
                    kwargs={'username': PostPagesTests.user.username}
                    ): PostPagesTests.user_tmp,
            reverse(PostPagesTests.post_url_name,
                    kwargs={'post_id': PostPagesTests.post.pk}
                    ): PostPagesTests.post_tmp,
            reverse(PostPagesTests.post_edit_url_name,
                    kwargs={'post_id': PostPagesTests.post.pk}
                    ): PostPagesTests.post_edit_tmp,
            reverse(PostPagesTests.post_create_url_name): (
                PostPagesTests.post_create_tmp),
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)


class PostPaginatorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.TOP_N_ENTRIES = 10
        cls.N_GENERATES_GROUP_1 = 16
        cls.N_GENERATES_GROUP_2 = 18
        cls.N_GENERATES_GROUP_3 = 14
        cls.user = User.objects.create_user(username='HasNoName')
        cls.user_2 = User.objects.create_user(username='HasName')
        cls.group_1 = Group.objects.create(
            title='group_1',
            slug='slug_1',
            description='description_1',
        )
        cls.group_2 = Group.objects.create(
            title='group_2',
            slug='slug_2',
            description='description_2',
        )
        bulk_list = list()
        for i in range(int(cls.N_GENERATES_GROUP_1)):
            bulk_list.append(
                Post(author=cls.user, text=f'text_{i}', group=cls.group_1)
            )
        for i in range(int(cls.N_GENERATES_GROUP_2)):
            bulk_list.append(
                Post(author=cls.user, text=f'text_{i}', group=cls.group_2)
            )
        for i in range(int(cls.N_GENERATES_GROUP_3)):
            bulk_list.append(
                Post(author=cls.user_2, text=f'text_{i}')
            )
        Post.objects.bulk_create(bulk_list)

        cls.index_url_name = 'posts:index'
        cls.group_url_name = 'posts:group_list'
        cls.user_url_name = 'posts:profile'

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostPaginatorTests.user)

    def test_static_first_page_contains_n_records(self):
        templates_url_names = (
            PostPaginatorTests.index_url_name,
        )
        for address in templates_url_names:
            with self.subTest(address=address):
                response = self.authorized_client.get(reverse(address))
                self.assertEqual(len(response.context['page_obj']),
                                 PostPaginatorTests.TOP_N_ENTRIES)

    def test_static_last_page_contains_n_records(self):
        templates_url_names = (
            PostPaginatorTests.index_url_name,
        )
        for address in templates_url_names:
            with self.subTest(address=address):
                response = self.authorized_client.get(
                    reverse(PostPaginatorTests.index_url_name) + '?page=-1'
                )
                self.assertEqual(len(response.context['page_obj']),
                                 ((PostPaginatorTests.N_GENERATES_GROUP_1
                                   + PostPaginatorTests.N_GENERATES_GROUP_2
                                   + PostPaginatorTests.N_GENERATES_GROUP_3) %
                                  PostPaginatorTests.TOP_N_ENTRIES))

    def test_dynamic_first_page_contains_n_records(self):
        templates_url_names_with_kwargs = {
            PostPaginatorTests.group_url_name: {
                'slug': PostPaginatorTests.group_1.slug
            },
            PostPaginatorTests.user_url_name: {
                'username': PostPaginatorTests.user_2.username
            },
        }
        for address, kwargs in templates_url_names_with_kwargs.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(
                    reverse(address, kwargs=kwargs)
                )
                self.assertEqual(len(response.context['page_obj']),
                                 PostPaginatorTests.TOP_N_ENTRIES)

    def test_dynamic_last_page_contains_n_records(self):
        templates_url_names_with_kwargs = {
            PostPaginatorTests.group_url_name: {
                'kwargs': {'slug': PostPaginatorTests.group_1.slug},
                'n_last_elements': (PostPaginatorTests.N_GENERATES_GROUP_1 %
                                    PostPaginatorTests.TOP_N_ENTRIES),
            },
            PostPaginatorTests.user_url_name: {
                'kwargs': {'username': PostPaginatorTests.user_2.username},
                'n_last_elements': (PostPaginatorTests.N_GENERATES_GROUP_3 %
                                    PostPaginatorTests.TOP_N_ENTRIES),
            },
        }
        for address, context in templates_url_names_with_kwargs.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(
                    reverse(address, kwargs=context['kwargs']) + '?page=-1'
                )
                self.assertEqual(len(response.context['page_obj']),
                                 context['n_last_elements'])


class PostContextTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.post = Post.objects.create(
            author=cls.user,
            text='test_text',
        )
        cls.post_edit_url_name = 'posts:post_edit'
        cls.post_create_url_name = 'posts:post_create'

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostContextTests.user)

    def test_form_edit_or_create(self):
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        template_url_for_post_forms = {
            'edit_url': reverse(
                PostContextTests.post_edit_url_name,
                kwargs={'post_id': PostContextTests.post.pk}
            ),
            'create_url': reverse(
                PostContextTests.post_create_url_name
            ),
        }
        for form_type, form_url in template_url_for_post_forms.items():
            with self.subTest('Form response'):
                response = self.authorized_client.get(form_url)
                for value, expected in form_fields.items():
                    with self.subTest(value=value):
                        form_field = response.context.get('form').fields.get(
                            value)
                        self.assertIsInstance(form_field, expected)


class FollowAccessTests(TestCase):
    """
    Авторизованный пользователь может подписываться на других пользователей
    и удалять их из подписок.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasName')
        cls.author1 = User.objects.create_user(username='Author1Name')
        cls.author2 = User.objects.create_user(username='Author2Name')
        cls.post1 = Post.objects.create(
            author=cls.author1,
            text='test_text_1',
        )
        cls.post2 = Post.objects.create(
            author=cls.author2,
            text='test_text_2',
        )
        Follow.objects.create(user=cls.user, author=cls.author1)
        Follow.objects.create(user=cls.user, author=cls.author2)

    def setUp(self):
        cache.clear()

    def test_subscription_possible(self):
        authors = Follow.objects.filter(
            user=FollowAccessTests.user
        ).values_list('author', flat=True)
        self.assertIn(FollowAccessTests.author1.pk, authors)
        self.assertIn(FollowAccessTests.author2.pk, authors)

    def test_unsubscription_possible(self):
        Follow.objects.get(user=FollowAccessTests.user,
                           author=FollowAccessTests.author1).delete()
        authors = Follow.objects.filter(
            user=FollowAccessTests.user
        ).values_list('author', flat=True)
        self.assertNotIn(FollowAccessTests.author1.pk, authors)
        self.assertIn(FollowAccessTests.author2.pk, authors)


class FollowFeedTests(TestCase):
    """
    Новая запись пользователя появляется в ленте тех, кто на него подписан
    и не появляется в ленте тех, кто не подписан.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_follower = User.objects.create_user(username='HasName1')
        cls.user_not_follower = User.objects.create_user(username='HasName2')
        cls.author = User.objects.create_user(username='AuthorName')
        cls.post = Post.objects.create(
            author=cls.author,
            text='test_text',
        )
        cls.following = Follow.objects.create(user=cls.user_follower,
                                              author=cls.author)
        cls.follow_index_url_name = 'posts:follow_index'

    def setUp(self):
        cache.clear()
        self.authorized_follower = Client()
        self.authorized_follower.force_login(FollowFeedTests.user_follower)
        self.authorized_not_follower = Client()
        self.authorized_not_follower.force_login(
            FollowFeedTests.user_not_follower
        )

    def test_post_in_subscribed_feed(self):
        response = self.authorized_follower.get(
            reverse(FollowFeedTests.follow_index_url_name))
        self.assertIn(FollowFeedTests.post,
                      response.context['page_obj'].object_list)

    def test_post_not_in_unsubscribed_feed(self):
        response = self.authorized_not_follower.get(
            reverse(FollowFeedTests.follow_index_url_name))
        self.assertNotIn(FollowFeedTests.post,
                         response.context['page_obj'].object_list)

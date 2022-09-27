import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache

from ..forms import PostForm, CommentForm
from ..models import Post, Comment


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.guest_user = User.objects.create_user(username='HasName')
        cls.post = Post.objects.create(
            author=cls.user,
            text='test_text',
        )
        cls.form = PostForm()
        cls.post_create_url_name = 'posts:post_create'
        cls.post_edit_url_name = 'posts:post_edit'
        cls.uploaded_gif = SimpleUploadedFile(
            name='small.gif',
            content=(
                b'\x47\x49\x46\x38\x39\x61\x02\x00'
                b'\x01\x00\x80\x00\x00\x00\x00\x00'
                b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                b'\x0A\x00\x3B'
            ),
            content_type='image/gif'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostCreateFormTests.user)

    def test_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'new_post_text',
            'image': PostCreateFormTests.uploaded_gif,
        }
        self.authorized_client.post(
            reverse(PostCreateFormTests.post_create_url_name),
            data=form_data,
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='new_post_text',
                author=PostCreateFormTests.user,
                image='posts/small.gif'
            ).exists()
        )

    def test_create_post_only_for_authorized(self):
        form_data = {
            'text': 'new_post_text',
        }
        self.guest_client.post(
            reverse(PostCreateFormTests.post_create_url_name),
            data=form_data,
        )
        self.assertFalse(
            Post.objects.filter(
                text='new_post_text',
                author=PostCreateFormTests.guest_user
            ).exists()
        )

    def test_edit_post(self):
        post_pk = PostCreateFormTests.post.pk
        form_data = {
            'text': 'new_post_text_updated',
        }
        self.authorized_client.post(
            reverse(PostCreateFormTests.post_edit_url_name,
                    kwargs={'post_id': post_pk}),
            data=form_data,
            follow=True,
        )
        response_new_text = Post.objects.filter(
            text='new_post_text_updated',
            author=PostCreateFormTests.user
        )

        self.assertFalse(
            Post.objects.filter(
                text='new_post_text',
                author=PostCreateFormTests.user
            ).exists()
        )
        self.assertEqual(len(list(response_new_text)), 1)
        self.assertEqual(response_new_text.first().pk, post_pk)


class CommentCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.guest_user = User.objects.create_user(username='HasName')
        cls.post = Post.objects.create(
            author=cls.user,
            text='test_text',
        )
        cls.comment_create_url_name = 'posts:add_comment'
        cls.form = CommentForm()

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(CommentCreateFormTests.user)

    def test_create_post_comment(self):
        post_pk = CommentCreateFormTests.post.pk
        comments_for_post_count = Comment.objects.filter(post=post_pk).count()
        form_data = {
            'text': 'new_post_comment_text',
        }
        self.authorized_client.post(
            reverse(CommentCreateFormTests.comment_create_url_name,
                    kwargs={'post_id': post_pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.filter(post=post_pk).count(),
                         comments_for_post_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                post=post_pk,
                text='new_post_comment_text',
                author=PostCreateFormTests.user,
            ).exists()
        )

    def test_create_post_comment_only_for_authorized(self):
        post_pk = CommentCreateFormTests.post.pk
        form_data = {
            'text': 'new_post_comment_text',
        }
        self.guest_client.post(
            reverse(CommentCreateFormTests.comment_create_url_name,
                    kwargs={'post_id': post_pk}),
            data=form_data,
            follow=True
        )
        self.assertFalse(
            Post.objects.filter(
                text='new_post_comment_text',
                author=CommentCreateFormTests.guest_user
            ).exists()
        )

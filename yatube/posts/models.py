from django.db import models
from django.contrib.auth import get_user_model
from core.models import CreatedModel


User = get_user_model()


class Group(models.Model):
    """Communities model."""

    title = models.CharField(verbose_name='Заголовок',
                             max_length=200,
                             help_text='Короткое название поста')
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(verbose_name='Описание',
                                   help_text='Текст поста')

    def __str__(self) -> str:
        return f"Group {self.title}"


class Post(CreatedModel):
    """Post model."""

    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='posts',
                               verbose_name='Автор')
    group = models.ForeignKey(Group,
                              blank=True,
                              null=True,
                              on_delete=models.SET_NULL,
                              related_name='posts',
                              verbose_name='Группа',
                              help_text=('Группа, к которой будет '
                                         'относиться пост'))

    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return f'{self.text[:15]}'


class Comment(CreatedModel):
    """Comments model."""
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='comments',
                             verbose_name='Комментарии',
                             help_text='Комментарий к посту')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='comments',
                               verbose_name='Автор',
                               help_text='Автор комментария')

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'{self.text[:15]}'


class Follow(CreatedModel):
    """Following authors' model."""
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='follower',
                             verbose_name='Пользователь',
                             help_text='Пользователь, осуществляющий подписку')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='following',
                               verbose_name='Автор',
                               help_text='Автор заказываемой подписки')

    class Meta:
        ordering = ('-author',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (models.UniqueConstraint(fields=['user', 'author'],
                                               name='unique_following'),)

from django.utils.translation import gettext_lazy as _
from django.forms import ModelForm
from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        labels = {
            'text': _('Текст'),
            'group': _('Название группы'),
            'image': _('Изображение')
        }
        help_texts = {
            'text': _('Здесь будет пост.'),
            'group': _('Здесь название группы.'),
            'image': _('Здесь изображение.')
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        labels = {
            'text': _('Текст'),
        }
        help_texts = {
            'text': _('Здесь будет комментарий.'),
        }

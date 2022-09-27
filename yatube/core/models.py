from django.db import models


class CreatedModel(models.Model):
    """Абстрактная модель. Добавляет дату создания."""
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        db_index=True
    )
    text = models.TextField(verbose_name='Текст',
                            help_text='Введите текст')

    class Meta:
        abstract = True

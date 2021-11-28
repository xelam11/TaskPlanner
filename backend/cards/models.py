from django.core.validators import MinValueValidator
from django.db import models

from boards.models import Tag
from lists.models import List
from users.models import CustomUser


class Card(models.Model):
    name = models.CharField(max_length=50,
                            verbose_name='Название',
                            help_text='Напишите название',
                            )
    description = models.TextField(verbose_name='Оисание',
                                   help_text='Напишите описание',
                                   blank=True,
                                   )
    list = models.ForeignKey(List,
                             on_delete=models.CASCADE,
                             related_name='cards',
                             verbose_name='Лист'
                             )
    participants = models.ManyToManyField(CustomUser,
                                          related_name='cards_participants',
                                          blank=True,
                                          verbose_name='Участники',
                                          )
    tags = models.ManyToManyField(Tag,
                                  related_name='cards',
                                  blank=True,
                                  verbose_name='Тег',
                                  )
    position = models.PositiveSmallIntegerField(
        verbose_name='Номер позиции на листе',
        blank=True,
        validators=[MinValueValidator(1), ]
    )

    class Meta:
        verbose_name = 'Карточка'
        verbose_name_plural = 'Карточки'
        ordering = ['position']

    def __str__(self):
        return self.name


class FileInCard(models.Model):
    file = models.FileField(upload_to='card_files',
                            verbose_name='Файл',
                            help_text='Загрузите файл',
                            )
    card = models.ForeignKey(Card,
                             on_delete=models.CASCADE,
                             related_name='files',
                             verbose_name='Карточка'
                             )

    class Meta:
        verbose_name = 'Файл в карточке'
        verbose_name_plural = 'Файлы в карточках'

    def __str__(self):
        return f'Файл: {self.file} => {self.card}'


class Comment(models.Model):
    author = models.ForeignKey(CustomUser,
                               on_delete=models.CASCADE,
                               related_name='comments',
                               verbose_name='Автор',
                               )
    text = models.TextField(verbose_name='Текст',
                            help_text='Напишите текст комментария',
                            )
    card = models.ForeignKey(Card,
                             on_delete=models.CASCADE,
                             related_name='comments',
                             verbose_name='Карточка',
                             )
    is_updated = models.BooleanField(default=False
                                     )
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата добавления')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:30]


class CheckList(models.Model):
    text = models.CharField(max_length=50,
                            verbose_name='Текст',
                            help_text='Напишите текст',
                            )
    card = models.ForeignKey(Card,
                             on_delete=models.CASCADE,
                             related_name='check_lists',
                             verbose_name='Карточка',
                             )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Чек-лист'
        verbose_name_plural = 'Чек-листы'

    def __str__(self):
        return self.text

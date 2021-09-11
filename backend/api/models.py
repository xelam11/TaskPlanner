from django.core.validators import MinValueValidator
from django.db import models

from users.models import CustomUser


class Board(models.Model):
    name = models.CharField(max_length=50,
                            verbose_name='Название',
                            help_text='Напишите название',
                            )
    description = models.TextField(verbose_name='Оисание',
                                   help_text='Напишите описание',
                                   blank=True,
                                   )
    author = models.ForeignKey(CustomUser,
                               on_delete=models.CASCADE,
                               related_name='boards_author',
                               verbose_name='Автор',
                               )
    participants = models.ManyToManyField(CustomUser,
                                          related_name='boards_participants',
                                          blank=True,
                                          verbose_name='Участники',
                                          )

    class Meta:
        verbose_name = 'Доска'
        verbose_name_plural = 'Доски'
        ordering = ['name']

    def __str__(self):
        return self.name


# class List(models.Model):
#     name = models.CharField(max_length=50,
#                             verbose_name='Название',
#                             help_text='Напишите название',
#                             )
#     board = models.ForeignKey(Board,
#                               on_delete=models.CASCADE,
#                               related_name='lists',
#                               verbose_name='Доска',
#                               )
#     position = models.PositiveSmallIntegerField(
#         verbose_name='Номер позиции на доске',
#         default=1,
#         validators=[MinValueValidator(1), ]
#     )
#
#     class Meta:
#         verbose_name = 'Список'
#         verbose_name_plural = 'Списки'
#
#     def __str__(self):
#         return self.name
#
#
# class Tag(models.Model):
#     name = models.CharField(max_length=50,
#                             verbose_name='Название цвета',
#                             help_text='Напишите название цвета',
#                             default='Белый',
#                             )
#     color = models.CharField(max_length=7,
#                              verbose_name='Код цвета',
#                              help_text='Напишите код цвета',
#                              default='#ffffff',
#                              unique=True,
#                              )
#
#     class Meta:
#         verbose_name = 'Тег'
#         verbose_name_plural = 'Теги'
#
#     def __str__(self):
#         return self.name
#
#
# class Card(models.Model):
#     name = models.CharField(max_length=50,
#                             verbose_name='Название',
#                             help_text='Напишите название',
#                             )
#     description = models.TextField(verbose_name='Оисание',
#                                    help_text='Напишите описание',
#                                    )
#     author = models.ForeignKey(CustomUser,
#                                on_delete=models.CASCADE,
#                                related_name='cards',
#                                verbose_name='Автор',
#                                )
#     participants = models.ManyToManyField(CustomUser,
#                                           related_name='cards',
#                                           blank=True,
#                                           verbose_name='Участники',
#                                           )
#     list = models.ForeignKey(List,
#                              on_delete=models.CASCADE,
#                              related_name='cards',
#                              verbose_name='Список',
#                              )
#     tags = models.ManyToManyField(Tag,
#                                   related_name='cards',
#                                   blank=True,
#                                   verbose_name='Тег',
#                                   )
#     files = models.FileField(upload_to='cards',
#                              verbose_name='Файл',
#                              help_text='Загрузите файл',
#                              )
#     position = models.PositiveSmallIntegerField(
#         verbose_name='Номер позиции в листе',
#         default=1,
#         validators=[MinValueValidator(1), ]
#     )
#
#     class Meta:
#         verbose_name = 'Карточка'
#         verbose_name_plural = 'Карточки'
#
#     def __str__(self):
#         return self.name
#
#
# class Comment(models.Model):
#     author = models.ForeignKey(CustomUser,
#                                on_delete=models.CASCADE,
#                                related_name='comments',
#                                verbose_name='Автор',
#                                )
#     text = models.TextField(verbose_name='Текст',
#                             help_text='Напишите текст комментария',
#                             )
#     card = models.CharField(Card,
#                             related_name='comments',
#                             verbose_name='Карточка',
#                             )
#     pub_date = models.DateTimeField(auto_now_add=True)
#
#     class Meta:
#         verbose_name = 'Комментарий'
#         verbose_name_plural = 'Комментарии'
#
#     def __str__(self):
#         return self.text

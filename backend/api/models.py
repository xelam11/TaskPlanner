from django.core.validators import MinValueValidator
from django.db import models

from users.models import CustomUser


class List(models.Model):
    name = models.CharField(max_length=50,
                            verbose_name='Название',
                            help_text='Напишите название',
                            )
    position = models.PositiveSmallIntegerField(
        verbose_name='Номер позиции на доске',
        blank=True,
        validators=[MinValueValidator(1), ]
    )

    class Meta:
        verbose_name = 'Список'
        verbose_name_plural = 'Списки'

    def __str__(self):
        return self.name


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


class Favorite(models.Model):
    user = models.ForeignKey(CustomUser,
                             on_delete=models.CASCADE,
                             related_name='favorite_subscriber',
                             verbose_name='Пользователь',
                             )
    board = models.ForeignKey(Board,
                              on_delete=models.CASCADE,
                              related_name='favorite_board',
                              verbose_name='Доска',
                              )
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата добавления',
                                    )

    class Meta:
        verbose_name = 'Избранный'
        verbose_name_plural = 'Избранные'
        constraints = [models.UniqueConstraint(
            fields=['user', 'board'],
            name='unique_favorites_boards')]

    def __str__(self):
        return (f'Пользователь: {self.user}, '
                f'избранные доски: {self.board.name}')
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

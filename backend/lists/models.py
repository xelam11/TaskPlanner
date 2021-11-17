from django.core.validators import MinValueValidator
from django.db import models

from boards.models import Board


class List(models.Model):
    name = models.CharField(max_length=50,
                            verbose_name='Название',
                            help_text='Напишите название',
                            )
    board = models.ForeignKey(Board,
                              on_delete=models.CASCADE,
                              related_name='lists',
                              verbose_name='Доска',
                              )
    position = models.PositiveSmallIntegerField(
        verbose_name='Номер позиции на доске',
        blank=True,
        validators=[MinValueValidator(1), ]
    )

    class Meta:
        verbose_name = 'Список'
        verbose_name_plural = 'Списки'
        ordering = ['position']

    def __str__(self):
        return self.name

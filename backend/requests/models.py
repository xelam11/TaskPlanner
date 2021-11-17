from django.db import models

from boards.models import Board
from users.models import CustomUser


class Request(models.Model):
    board = models.ForeignKey(Board,
                              on_delete=models.CASCADE,
                              related_name='requesting_board',
                              verbose_name='Доска',
                              )
    user = models.ForeignKey(CustomUser,
                             on_delete=models.CASCADE,
                             related_name='requested_participant',
                             verbose_name='Участник')

    class Meta:
        verbose_name = 'Запрос'
        verbose_name_plural = 'Запросы'
        constraints = [models.UniqueConstraint(
            fields=['board', 'user'],
            name='unique_requests')]

    def __str__(self):
        return (f'Доска: {self.board}, '
                f'запрашиваемый пользователь: {self.user}')

from django.db import models

from users.models import CustomUser


class BoardManager(models.Manager):

    def create_board(self, author, **kwargs):
        current_user = author
        board = Board.objects.create(author=current_user, **kwargs)
        ParticipantInBoard.objects.create(board=board,
                                          participant=current_user,
                                          is_moderator=True)

        for color in Tag.Color.values:
            Tag.objects.create(color=color, board=board)

        return board


class Board(models.Model):
    name = models.CharField(max_length=50,
                            verbose_name='Название',
                            help_text='Напишите название',
                            )
    description = models.TextField(verbose_name='Оисание',
                                   help_text='Напишите описание',
                                   blank=True,
                                   )
    avatar = models.ImageField(upload_to='board_avatars',
                               blank=True,
                               verbose_name='Аватар',
                               help_text='Загрузите аватар'
                               )
    author = models.ForeignKey(CustomUser,
                               on_delete=models.CASCADE,
                               related_name='boards_author',
                               verbose_name='Автор',
                               )
    participants = models.ManyToManyField(CustomUser,
                                          through='ParticipantInBoard',
                                          related_name='boards_participants',
                                          blank=True,
                                          verbose_name='Участники',
                                          )
    objects = BoardManager()

    class Meta:
        verbose_name = 'Доска'
        verbose_name_plural = 'Доски'
        ordering = ['name']

    def __str__(self):
        return self.name


class Tag(models.Model):
    class Color(models.IntegerChoices):
        RED = 1
        ORANGE = 2
        YELLOW = 3
        GREEN = 4
        BLUE = 5
        PURPLE = 6

    color_to_hex = {
        Color.RED: '#f35a5a',
        Color.ORANGE: '#ff9b63',
        Color.YELLOW: '#fdff97',
        Color.GREEN: '#9bc665',
        Color.BLUE: '#67b5fd',
        Color.PURPLE: '#c173ff'
    }

    name = models.CharField(max_length=20,
                            verbose_name='Название тега',
                            help_text='Напишите название тега',
                            blank=True,
                            default=''
                            )
    color = models.PositiveSmallIntegerField(choices=Color.choices
                                             )
    board = models.ForeignKey(Board,
                              on_delete=models.CASCADE,
                              related_name='tags',
                              verbose_name='Доска',
                              )

    @property
    def hex(self):
        return Tag.color_to_hex[self.color]

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return f"Color: '{self.color}', name: '{self.name}'"


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


class ParticipantInBoard(models.Model):
    board = models.ForeignKey(Board,
                              on_delete=models.CASCADE,
                              verbose_name='Доска',
                              )
    participant = models.ForeignKey(CustomUser,
                                    on_delete=models.CASCADE,
                                    verbose_name='Участник'
                                    )
    is_moderator = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Участник в доске'
        verbose_name_plural = 'Участники в досках'

    def __str__(self):
        return f'Участник: {self.participant} => {self.board}'

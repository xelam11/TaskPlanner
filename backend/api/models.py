from django.core.validators import MinValueValidator
from django.db import models

from users.models import CustomUser


class Tag(models.Model):
    name = models.CharField(max_length=20,
                            verbose_name='Название цвета',
                            help_text='Напишите название цвета',
                            unique=True
                            )
    color = models.CharField(max_length=7,
                             verbose_name='Код цвета (HEX)',
                             help_text='Напишите код цвета (HEX)',
                             unique=True,
                             )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class BoardManager(models.Manager):

    def create_board(self, author, **kwargs):
        current_user = author

        board = Board.objects.create(author=current_user, **kwargs)
        board.participants.add(current_user)

        participant_in_board = ParticipantInBoard.objects.get(
            board=board,
            participant=current_user)
        participant_in_board.is_moderator = True
        participant_in_board.save()

        for tag in Tag.objects.all():
            TagInBoard.objects.create(board=board, tag=tag)

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
    tags = models.ManyToManyField(Tag,
                                  through='TagInBoard',
                                  related_name='boards',
                                  blank=True,
                                  verbose_name='Тег',
                                  )

    objects = BoardManager()

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


class ParticipantRequest(models.Model):
    board = models.ForeignKey(Board,
                              on_delete=models.CASCADE,
                              related_name='requesting_board',
                              verbose_name='Доска',
                              )
    participant = models.ForeignKey(CustomUser,
                                    on_delete=models.CASCADE,
                                    related_name='requested_participant',
                                    verbose_name='Участник')

    class Meta:
        verbose_name = 'Запрос'
        verbose_name_plural = 'Запросы'
        constraints = [models.UniqueConstraint(
            fields=['board', 'participant'],
            name='unique_requests')]

    def __str__(self):
        return (f'Доска: {self.board}, '
                f'запрашиваемый пользователь: {self.participant}')


class TagInBoard(models.Model):
    tag = models.ForeignKey(Tag,
                            on_delete=models.CASCADE,
                            verbose_name='Тег',
                            )
    board = models.ForeignKey(Board,
                              on_delete=models.CASCADE,
                              verbose_name='Доска'
                              )
    content = models.CharField(max_length=20,
                               blank=True,
                               default='',
                               verbose_name='Содержание',
                               help_text='Напишите содержание')

    class Meta:
        verbose_name = 'Тег в доске'
        verbose_name_plural = 'Теги в досках'

    def __str__(self):
        return f'Тег: {self.tag} (содержание: {self.content}) => {self.board}'


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
    # tags = models.ManyToManyField(Tag,
    #                               related_name='cards',
    #                               blank=True,
    #                               verbose_name='Тег',
    #                               )
    files = models.FileField(upload_to='cards',
                             blank=True,
                             verbose_name='Файл',
                             help_text='Загрузите файл',
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

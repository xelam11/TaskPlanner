# Generated by Django 3.2.6 on 2021-11-13 15:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Board',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Напишите название', max_length=50, verbose_name='Название')),
                ('description', models.TextField(blank=True, help_text='Напишите описание', verbose_name='Оисание')),
                ('avatar', models.ImageField(blank=True, help_text='Загрузите аватар', upload_to='board_avatars', verbose_name='Аватар')),
            ],
            options={
                'verbose_name': 'Доска',
                'verbose_name_plural': 'Доски',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')),
            ],
            options={
                'verbose_name': 'Избранный',
                'verbose_name_plural': 'Избранные',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='', help_text='Напишите название тега', max_length=20, verbose_name='Название тега')),
                ('color', models.PositiveSmallIntegerField(choices=[(1, 'Red'), (2, 'Orange'), (3, 'Yellow'), (4, 'Green'), (5, 'Blue'), (6, 'Purple')])),
                ('board', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tags', to='boards.board', verbose_name='Доска')),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
            },
        ),
        migrations.CreateModel(
            name='ParticipantInBoard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_moderator', models.BooleanField(default=False)),
                ('board', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='boards.board', verbose_name='Доска')),
            ],
            options={
                'verbose_name': 'Участник в доске',
                'verbose_name_plural': 'Участники в досках',
            },
        ),
    ]

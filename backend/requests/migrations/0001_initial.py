# Generated by Django 3.2.6 on 2021-11-14 09:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('boards', '0002_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('board', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requesting_board', to='boards.board', verbose_name='Доска')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requested_participant', to=settings.AUTH_USER_MODEL, verbose_name='Участник')),
            ],
            options={
                'verbose_name': 'Запрос',
                'verbose_name_plural': 'Запросы',
            },
        ),
        migrations.AddConstraint(
            model_name='request',
            constraint=models.UniqueConstraint(fields=('board', 'user'), name='unique_requests'),
        ),
    ]
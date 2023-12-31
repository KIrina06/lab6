# Generated by Django 4.2.4 on 2023-12-13 21:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('name', models.CharField(max_length=30)),
                ('is_moderator', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
            },
        ),
        migrations.CreateModel(
            name='Expertises',
            fields=[
                ('expertise_id', models.AutoField(primary_key=True, serialize=False)),
                ('picture', models.CharField(blank=True, null=True)),
                ('title', models.CharField(blank=True, max_length=70, null=True, unique=True)),
                ('price', models.CharField(blank=True, null=True)),
                ('context', models.CharField(blank=True, null=True)),
                ('expertise_status', models.IntegerField(choices=[(1, 'Действует'), (2, 'Удалена')], default=1)),
            ],
        ),
        migrations.CreateModel(
            name='Requests',
            fields=[
                ('request_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('closed_date', models.DateTimeField(blank=True, null=True)),
                ('created_date', models.DateTimeField(blank=True, null=True)),
                ('formated_date', models.DateTimeField(blank=True, null=True)),
                ('req_status', models.IntegerField(choices=[(1, 'Черновик'), (2, 'В работе'), (3, 'Завершен'), (4, 'Отклонен'), (5, 'Удален')], default=1)),
                ('moder_id', models.IntegerField(blank=True, null=True)),
                ('expertises', models.ManyToManyField(to='painting.expertises')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ReqExps',
            fields=[
                ('re_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('expertise', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='painting.expertises')),
                ('request', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='painting.requests')),
            ],
            options={
                'unique_together': {('expertise', 'request')},
            },
        ),
    ]

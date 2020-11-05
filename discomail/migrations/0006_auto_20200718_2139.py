# Generated by Django 3.0.5 on 2020-07-18 21:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('discomail', '0005_auto_20200715_1005'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emaillog',
            name='email_status',
            field=models.CharField(choices=[('SUC', 'Success'), ('ERR', 'Error'), ('NA', 'Not Available')], default='NA', max_length=3),
        ),
        migrations.AlterField(
            model_name='emailqueue',
            name='email_status',
            field=models.CharField(choices=[('SUC', 'Success'), ('ERR', 'Error'), ('NA', 'Not Available')], default='NA', max_length=3),
        ),
        migrations.CreateModel(
            name='PlatformInvite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invite_hash', models.CharField(default='random_invite_hash', max_length=255)),
                ('used', models.BooleanField(default=False)),
                ('used_on_datetime', models.DateTimeField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('email_log', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='platform_invite', to='discomail.EmailLog')),
                ('email_queue', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='platform_invite', to='discomail.EmailQueue')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='platform_invite', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Platform Invite',
                'verbose_name_plural': 'Platform Invites',
            },
        ),
    ]
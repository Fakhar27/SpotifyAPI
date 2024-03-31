# Generated by Django 5.0.3 on 2024-03-31 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spotify', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpotifyUserInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('display_name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('filter_enabled', models.BooleanField(default=False)),
                ('filter_locked', models.BooleanField(default=False)),
                ('spotify_url', models.URLField()),
                ('followers_count', models.IntegerField(default=0)),
                ('playlists_data', models.JSONField(default=list)),
                ('followed_artists_data', models.JSONField(default=list)),
            ],
        ),
        migrations.DeleteModel(
            name='SpotifyData',
        ),
    ]
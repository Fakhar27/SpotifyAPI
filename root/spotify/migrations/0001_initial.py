# Generated by Django 5.0.3 on 2024-03-30 14:19

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FormDataModel',
            fields=[
                ('_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('firstName', models.CharField(max_length=100)),
                ('lastName', models.CharField(max_length=100)),
                ('contactNumber', models.CharField(max_length=15)),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='SpotifyData',
            fields=[
                ('_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('user_id', models.CharField(max_length=255)),
                ('country', models.CharField(max_length=50)),
                ('playlist_names', models.JSONField()),
                ('followed_artists', models.TextField()),
                ('top_tracks_country', models.TextField()),
                ('top_tracks', models.TextField()),
                ('saved_tracks', models.TextField()),
                ('saved_albums', models.TextField()),
                ('recommendations', models.TextField()),
            ],
        ),
    ]
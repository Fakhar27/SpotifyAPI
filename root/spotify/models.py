from django.db import models
import uuid

class SpotifyUserInfo(models.Model):
    display_name = models.CharField(max_length=255)
    email = models.EmailField()
    filter_enabled = models.BooleanField(default=False)
    filter_locked = models.BooleanField(default=False)
    spotify_url = models.URLField()
    followers_count = models.IntegerField(default=0)
    playlists_data = models.JSONField(default=list)
    followed_artists_data = models.JSONField(default=list)
    tracks_data = models.JSONField(default=list)

    def __str__(self):
        return self.display_name


class FormDataModel(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


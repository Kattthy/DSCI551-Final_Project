from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Genre(models.Model):
    #id = models.IntegerField(primary_key = True)
    name = models.CharField(max_length=100, null=False, blank=False)
    def __str__(self):
        return self.name

class Style(models.Model):
    #id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, null=False, blank=False)
    def __str__(self):
        return self.name

class Artist(models.Model):
    #id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, null=False, blank=False)
    def __str__(self):
        return self.name

class Picture(models.Model):
    #id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=512, primary_key=True, default='DEFAULT VALUE')
    url_path = models.CharField(max_length=512, default='DEFAULT VALUE')
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True)
    style = models.ForeignKey(Style, on_delete=models.SET_NULL, null=True, blank=True)
    artist = models.ForeignKey(Artist, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(null=False, blank=False)

class Features(models.Model):
    image = models.ForeignKey(Picture, on_delete=models.SET_NULL, null=True, blank=True)
    height = models.BigIntegerField(blank=True, null=True)
    width = models.BigIntegerField(blank=True, null=True)
    nchannels = models.BigIntegerField(db_column='nChannels', blank=True, null=True)  # Field name made lowercase.
    mode = models.BigIntegerField(blank=True, null=True)
    sift = models.TextField(blank=True, null=True)
    color_moments = models.TextField(blank=True, null=True)
    color_gist = models.TextField(blank=True, null=True)

class Predict_option(models.Model):
    #id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, null=False, blank=False)

class Prediction(models.Model):
    image = models.ImageField(null=False, blank=False)
    url_path = models.CharField(max_length=512, default='DEFAULT VALUE')
    predict_option = models.ForeignKey(Predict_option, on_delete=models.SET_NULL, null=True, blank=True)
    predict_result = models.TextField(blank=True, null=True)

class Predict_features(models.Model):
    image_id = models.CharField(max_length=512, default='DEFAULT VALUE')
    height = models.BigIntegerField(blank=True, null=True)
    width = models.BigIntegerField(blank=True, null=True)
    nchannels = models.BigIntegerField(db_column='nChannels', blank=True, null=True)  # Field name made lowercase.
    mode = models.BigIntegerField(blank=True, null=True)
    sift = models.TextField(blank=True, null=True)
    color_moments = models.TextField(blank=True, null=True)
    color_gist = models.TextField(blank=True, null=True)
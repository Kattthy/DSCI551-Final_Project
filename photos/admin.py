from django.contrib import admin

# Register your models here.
from .models import Genre, Style, Artist, Picture, Features, Prediction, Predict_option

admin.site.register(Genre)
admin.site.register(Style)
admin.site.register(Artist)
admin.site.register(Picture)
admin.site.register(Features)
admin.site.register(Prediction)
admin.site.register(Predict_option)
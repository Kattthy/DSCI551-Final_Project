from django.urls import path
from . import views

urlpatterns = [
    path('', views.album, name = 'album'),
    #path('<str:pagenum>/', views.album, name = 'album'),
    path('predict/', views.predict, name = 'predict'),
    path('upload/', views.upload, name = 'upload'),
    path('picture/<str:pk>/', views.viewPicture, name='picture'),
    path('extract/<str:pk>/', views.extract, name='extract'),
]
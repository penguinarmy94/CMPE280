from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('latest', views.latest, name='latest'),
    path('GetData', views.GetPastData, name='GetData'),
]
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('current', views.current, name='latest'),
    path('past', views.past, name='past'),
    path('future', views.future, name='future'),
    path('load', views.updatePast, name='load')
]
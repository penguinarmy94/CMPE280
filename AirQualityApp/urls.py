from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('latest', views.latest, name='latest'),
    path('future', views.future, name='future'),
    path('load', views.updatePast, name='load'),
    path('GetData', views.GetPastData, name='GetData'),
    path('verifyEmailAndZipcode', views.verifyEmailAndZipcode, name='verifyEmailAndZipcode'),
    path('subscription', views.subscription, name='subscription')
]

from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name = 'index'),
    path('application/', views.application, name = 'application'),
    path('launch/', views.launch, name = 'launch'),
    path('result/', views.result, name = 'result'),
]

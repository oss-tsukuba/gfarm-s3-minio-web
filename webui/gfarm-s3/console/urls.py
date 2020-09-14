from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name = 'index'),
    path('login/', views.login, name = 'login'),
    path('result/', views.result, name = 'result'),
    path('list/', views.list, name = 'list'),
    path('aclfile/', views.aclfile, name = 'aclfile'),
    path('chgkey/', views.aclfile, name = 'chgkey'),
    path('stop/', views.aclfile, name = 'stop'),
]

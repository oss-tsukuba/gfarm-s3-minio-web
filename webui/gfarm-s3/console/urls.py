from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.login, name = 'login'),
    path('logout/', views.logout, name = 'logout'),
    path('reauth/', views.reauth, name = 'reauth'),
    path('result/', views.result, name = 'result'),
    path('list/', views.list, name = 'list'),
    path('aclfile/', views.aclfile, name = 'aclfile'),
    path('chgkey/', views.chgkey, name = 'chgkey'),
    path('starts3/', views.starts3, name = 'starts3'),
    path('stops3/', views.stops3, name = 'stops3'),
    path('', views.result, name = 'other'),
]

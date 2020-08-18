from django.urls import path

from . import views

urlpatterns = [
    # ex: /console/
    path('', views.index, name = 'index'),

    # ex: /console/application/
    path('application/', views.application, name = 'application'),

    # ex: /console/launch/
    path('launch/', views.launch, name = 'launch'),

    # ex: /console/5/result/
    path('<int:status_id>/result/', views.result, name = 'result'),

]

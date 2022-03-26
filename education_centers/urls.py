from django.urls import path

from . import views

urlpatterns = [
    path('import/programs/', views.import_programs, name="import_programs"),

    path('trainers/', views.trainers_list, name="trainers_list"),
    path('trainers/add', views.add_trainer, name="add_trainer"),
    path('workshops/', views.workshops_list, name="workshops_list"),
    path('workshops/add', views.add_workshop, name="add_workshop")
]
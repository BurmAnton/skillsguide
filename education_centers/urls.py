from django.urls import path

from . import views

urlpatterns = [
    path('import/programs/', views.import_programs, name="import_programs"),
    path('assesment/add/all/', views.add_assesment_all, name="add_assesment_all"),
    #ЦО
    path('trainers/', views.trainers_list, name="trainers_list"),
    path('trainers/add', views.add_trainer, name="add_trainer"),
    path('workshops/', views.workshops_list, name="workshops_list"),
    path('workshops/add', views.add_workshop, name="add_workshop"),
    #Преподователь
    path('trainer/profile/<int:trainer_id>/<int:page_number>', views.trainer_profile, name='trainer_profile'),
    path('trainer/add_zoom_link/', views.add_zoom_link, name='add_zoom_link'),
    path('trainer/assessment/set', views.set_assessment, name='set_assessment'),
]
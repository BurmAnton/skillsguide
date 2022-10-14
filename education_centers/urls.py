from django.urls import path

from . import views

urlpatterns = [
    path('import/', views.import_ed_centers, name='import_ed_centers'),
    path('add/', views.add_ed_center, name='add_ed_center'),

    path('add/program/', views.add_program, name='add_program'),
    path('add/trainer/', views.add_trainer, name='add_trainer'),

    path('import/programs/', views.import_programs, name="import_programs"),
    #ЦО
    path('dashboard/<int:ed_center_id>/', views.ed_center_dashboard, name="ed_center_dashboard"),
    path('dashboard/<int:ed_center_id>/<str:message>', views.ed_center_dashboard, name="ed_center_dashboard"),
    path('trainers/', views.trainers_list, name="trainers_list"),
    path('trainers/add', views.add_trainer, name="add_trainer"),
    path('workshops/', views.workshops_list, name="workshops_list"),
    path('workshops/add', views.add_workshop, name="add_workshop"),
    #Преподователь
    path('trainer/profile/<int:trainer_id>/<int:page_number>', views.trainer_profile, name='trainer_profile'),
    path('trainer/add_zoom_link/', views.add_zoom_link, name='add_zoom_link'),
    path('trainer/assessment/set', views.set_assessment, name='set_assessment'),
]

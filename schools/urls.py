from django.urls import path

from . import views

urlpatterns = [
    path('profile/<int:school_id>/', views.school_profile, name='school_profile'),
    path('change/', views.change_school, name='change_school'),
    path('profile/<int:school_id>/grades/', views.grades_list, name='grades_list'),
    path('profile/<int:school_id>/grade/<int:grade_id>', views.grade, name='grade'),
    path('add', views.add_school, name='add_school'),
    path('import', views.import_schools, name='import_schools')
]

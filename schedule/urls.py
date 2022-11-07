from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('bundles/', views.bundles_list, name='bundles_list'),
    path('create/cycle/', views.create_cycle, name='create_cycle'),
    path('student/profile/<int:user_id>/', views.student_profile, name='student_profile'),
]

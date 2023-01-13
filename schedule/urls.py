from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('fill/tests/', views.fill_test, name='fill_test'),
    path('add_soft_skills/', views.add_soft_skills, name='add_soft_skills'),
    path('fix/attendance/', views.fix_attendance, name='fix_attendance'),
    path('bundles/', views.bundles_list, name='bundles_list'),
    path('stream/schedule/<int:stream_id>/', views.stream_schedule, name='stream_schedule'),
    path('create/cycle/', views.create_cycle, name='create_cycle'),
    path('student/profile/<int:user_id>/', views.student_profile, name='student_profile'),

    path('cycles/add_students/', views.add_students, name='add_students'),
]

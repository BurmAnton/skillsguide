from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create/cycle', views.create_cycle, name='create_cycle'),
    path('bundle/<int:bundle_id>/streams/fill', views.streams_fill, name='streams_fill'),
    path('bundle/<int:bundle_id>/slots/fill', views.slots_fill, name='slots_fill'),

    path('student/profile/<int:user_id>/', views.student_profile, name='student_profile'),
    path('student/change/profile/', views.change_profile_student, name='change_profile_student'),
    path('student/choose/bundle/', views.choose_bundle, name='choose_bundle'),

    path('ed_center/<int:ed_center_id>/bundles', views.bundles, name="bundles"),
    path('ed_center/<int:ed_center_id>/bundle/<int:bundle_id>/competencies', views.competencies, name="competencies"),
    path('ed_center/<int:ed_center_id>/bundle/<int:bundle_id>/competence/<int:competence_id>', views.competence_schedule, name='competence_schedule'),

    path('school/profile/<int:school_id>/', views.school_profile, name='school_profile'),
    path('school/student/dismissal/', views.student_dismissal, name='student_dismissal'),
    path('school/change/', views.change_school, name='change_school'),

    path('dashboard/students', views.student_dashboard, name="student_dashboard")
]

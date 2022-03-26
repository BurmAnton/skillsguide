from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create/cycle', views.create_cycle, name='create_cycle'),

    path('student/profile/<int:user_id>/', views.student_profile, name='student_profile'),

    path('ed_center/<int:ed_center_id>/bundles', views.bundles, name="bundles"),
    path('ed_center/<int:ed_center_id>/bundle/<int:bundle_id>/competencies', views.competencies, name="competencies"),
    path('ed_center/<int:ed_center_id>/bundle/<int:bundle_id>/competence/<int:competence_id>', views.competence_schedule, name='competence_schedule'),

    path('dashboard/students', views.student_dashboard, name="student_dashboard")
]
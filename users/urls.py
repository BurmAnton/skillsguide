from django.urls import path

from . import views

urlpatterns = [
    #auth
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    #registration
    path('registration/', views.registration, name='registration'),
    path('registration/choice/', views.reg_choice, name='reg_choice'),
    path('registration/<str:choice>/<int:stage>', views.reg_stage, name='reg_stage'),
    #pass_recovery
    path('password/recovery/<int:step>/', views.password_recovery, name="password_recovery"),
    #import
    path('import/students', views.import_students_coordinator, name="import_students_coordinator"),
    #export
    path('export/students/report', views.students_report, name="students_report"),
    #mailing
    path('mailing/form', views.mailing_form, name="mailing_form"),
    path('send/password/trainers', views.trainers_send_password, name="trainers_send_password")
]

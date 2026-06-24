from django.urls import path, include
from . import views
from .views import DeleteAccountView, RememberMeLoginView

urlpatterns = [
    # Home
    path('', views.homeView.as_view(), name='home'),

    # Auth
    path('login/', RememberMeLoginView.as_view(), name='login'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('userprofile/', views.userprofileView.as_view(), name='userprofile'),
    path('delete-account/', DeleteAccountView.as_view(), name='delete_account'),

    # Documentation
    path('documentation/', views.documentationView, name='documentation'),

    # Interview
    path('interview/', views.interview, name='interview'),
    path('interview/save/', views.interview_save, name='interview_save'),

    # Questions (FIXED HERE)
    path('add_questions/', views.add_question, name='add_questions'),
    path('questions/', views.question_list, name='question_list'),
    path('questions/delete/<int:pk>/', views.delete_question, name='delete_question'),

    # Categories
    path('categories/', views.create_category, name='categories'),
    path('category/delete/<int:pk>/', views.delete_category, name='delete_category'),

    # Packs
    path('create-pack/', views.create_pack, name='create_pack'),

    # Applications
    path('applications/', views.applications, name='applications'),
    path('applications/<int:pk>/', views.application_detail, name='application_detail'),
    path('application_review/', views.application_review, name='applications_review'),
    path('applicant-form/<int:pack_id>/', views.applicant_form, name='applicant_form'),

    # Approve / Deny
    path('applications/<int:id>/approve/', views.approve_application, name='approve_application'),
    path('applications/<int:id>/deny/', views.deny_application, name='deny_application'),

    # Error pages
    path('404/', views.Custom404View.as_view(), name='404'),
    path('500/', views.Custom500View.as_view(), name='500'),
]
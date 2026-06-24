from django.urls import path
from . import views
from .views import DeleteAccountView, RememberMeLoginView

urlpatterns = [
    # Core authentication and user management
    path('', views.homeView.as_view(), name='home'),
    path('login/', RememberMeLoginView.as_view(), name='login'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('userprofile/', views.userprofileView.as_view(), name='userprofile'),
    path('documentation/', views.documentationView, name='documentation'),
    path('interview/', interview, name = "interview"),
    path('add_questions/', views.add_question, name="add_questions"),

    path("signup/", views.SignUpView.as_view(), name="signup"),

    path('404', views.Custom404View.as_view(), name='404'),
    path('500', views.Custom500View.as_view(), name='500'),

    path('interview/', interview, name='interview'),
    path('delete-account/', DeleteAccountView.as_view(), name='delete_account'),

    # Knowledge and question administration
    path('documentation/', views.documentationView, name='documentation'),
    path('interview/', views.interview, name='interview'),
    path('add_questions/', views.add_questions, name='add_questions'),
    path('categories/', views.create_category, name='categories'),
    path('create-pack/', views.create_pack, name='create_pack'),

    # Application submission & review workflows
    path('applications/', views.applications, name='applications'),
    path('application_review/', views.application_review, name='applications_review'),
    path('applicant-form/<int:pack_id>/', views.applicant_form, name='applicant_form'),

    path('categories/', views.create_category, name='categories'),
    path("category/delete/<int:pk>/",views.delete_category,name="delete_category"),

    path('applications/<int:pk>/', views.application_detail, name='application_detail'),
    
    # Accept/Deny dynamic endpoints
    path('applications/<int:id>/approve/', views.approve_application, name='approve_application'),
    path('applications/<int:id>/deny/', views.deny_application, name='deny_application'),

    path('404', views.Custom404View.as_view(), name='404'),
    path('500', views.Custom500View.as_view(), name='500'),
    path("questions/", views.question_list, name="question_list"),
    path("questions/delete/<int:pk>/", views.delete_question, name="delete_question"),
    path('interview/save/', views.interview_save, name='interview_save'),
]
]

    path("questions/delete/<int:pk>/", views.delete_question, name="delete_question"),
]

from django.urls import path
from . import views
from .views import interview

from .views import interview

from .views import applications


urlpatterns = [

    path('', views.homeView.as_view(), name='home'),
    path('userprofile/', views.userprofileView.as_view(), name='userprofile'),
    path('documentation/', views.documentationView, name='documentation'),
    path('interview/', interview, name = "interview"),

    path("signup/", views.SignUpView.as_view(), name="signup"),

    path('404', views.Custom404View.as_view(), name='404'),
    path('500', views.Custom500View.as_view(), name='500'),
<<<<<<< HEAD
    
    ]
=======


    path('create-pack/', views.create_pack, name='create_pack'),
    path('applications/', views.applications, name='applications')

]
>>>>>>> 77fbbb5ac5cde2d8481e03a35e53ee8f3cad4f8c

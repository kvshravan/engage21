from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='student-home'),
    path('logout/', views.logout, name="student-logout"),
    path('dashboard/', views.dashboard, name="student-dashboard"),
    path('signup/', views.signUp, name='student-signup'),
    path('view/<slug:slug>/', views.view_assignment,
         name='student-view'),
    path('submit/<slug:slug>/', views.submit_assignment,
         name='student-submit'),
]

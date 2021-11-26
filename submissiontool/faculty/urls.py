from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="faculty-home"),
    path('logout/', views.logout, name="faculty-logout"),
    path('dashboard/', views.dashboard, name="faculty-dashboard"),
    path('create/', views.createAssignment, name="faculty-create"),
    path('view/<slug:slug>/', views.view_submissions,
         name='faculty-view'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="faculty-home"),
    path('logout/', views.logout, name="faculty-logout"),
    path('dashboard/', views.dashboard, name="faculty-dashboard"),
    path('create/', views.createAssignment, name="faculty-create"),
    path('reset/', views.reset_password, name="faculty-reset"),
    path('admin/', views.admin, name="faculty-admin"),
    path('view/<slug:slug>/', views.view_submissions,
         name='faculty-view'),
    path('delete/<slug:aid>/', views.delete,
         name='faculty-delete'),
    path('edit/<slug:slug>/', views.extend_deadline,
         name='faculty-extend'),
    path('evaluate/<slug:asid>/<slug:sid>/', views.evaluate_submission,
         name='faculty-evaluate'),
]

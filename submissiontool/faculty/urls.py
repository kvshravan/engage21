from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name="home"),
    path('logout/',views.logout,name="logout"),
    path('dashboard/',views.dashboard,name="dashboard"),
    path('create/',views.createAssignment,name="create"),
]

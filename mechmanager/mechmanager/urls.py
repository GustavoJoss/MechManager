from django.contrib import admin
from django.urls import path
from core import views                   # <-- ESSA LINHA FALTAVA
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
     path("logout/", views.logout_view, name="logout"),
    path("area/", views.user_area, name="user_area"),
]
from django.contrib import admin
from django.urls import path
from core import views              
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("area/", views.user_area, name="user_area"),
    path("vehicles/new/", views.vehicle_create, name="vehicle_create"),
    path("orders/new/", views.workorder_create, name="workorder_create"),
    path("orders/<int:pk>/confirm/", views.confirm_workorder, name="confirm_workorder"),
    path("os/<int:pk>/confirmar/", views.confirmar_os_json, name="confirmar_os_json"),
    path("profile/", views.profile, name="profile"),
    path("perfil/editar/", views.profile_edit, name="profile_edit"), 
    path("orders/<int:pk>/", views.workorder_detail, name="workorder_detail"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
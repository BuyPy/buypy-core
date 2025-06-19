"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from djoser.views import UserViewSet
from rest_framework.routers import DefaultRouter

urlpatterns = []
router = DefaultRouter()
router.register("users", UserViewSet, basename="users")

DEF_BLOCKED = settings.DJOSER.get("BLOCKED_ROUTS", [])

safe_patterns = [
    p for p in router.urls if not any(b in str(p.pattern) for b in DEF_BLOCKED)
]

urlpatterns += [
    path("auth/", include("djoser.urls.jwt")),
    path("auth/", include((safe_patterns, "djoser"), namespace="djoser")),
    path("admin/", admin.site.urls),
]

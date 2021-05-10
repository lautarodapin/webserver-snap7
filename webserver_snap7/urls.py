"""webserver_snap7 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.contrib import admin
from django.db.models import base
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.shortcuts import render

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", include("app.urls")),
    path("", lambda r: render(r, "index.html")),
    path('test/', lambda r: render(r, "app/index.html")),
    path('test-2/', lambda r: render(r, "app/dato_procesado.html")),
    path('graficos-rest/', lambda r: render(r, "app/graficos_rest.html")),
] 

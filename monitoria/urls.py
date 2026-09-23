from django.urls import path

from . import views

app_name = "artigos"

urlpatterns = [
    path("", views.index, name="lista"),
    ]
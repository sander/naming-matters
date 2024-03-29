from django.urls import path

from . import views


app_name = "naming"
urlpatterns = [
    path("", views.index, name="index"),
    path("<uuid:concept_key>/", views.detail, name="detail"),
    path("_new/", views.new, name="new"),
    path("_edit/<uuid:concept_key>/", views.edit, name="edit"),
    path("_export/", views.export, name="export"),
    path("_settings/", views.settings, name="settings"),
    path("_oauth2/callback/", views.oauth2_callback, name="oauth2callback"),
]

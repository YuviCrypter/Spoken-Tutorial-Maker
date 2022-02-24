from django.urls import path
from Site import views

urlpatterns = [
    path("", views.index, name="index"),
    path("Site/upload", views.upload, name ="upload"),
    path("Site/voice", views.voice, name = "voice"),
    path("Site/video", views.videoupload, name = "videoupload"),
    path("Site/upload/preview",views.preview, name="preview"),
]
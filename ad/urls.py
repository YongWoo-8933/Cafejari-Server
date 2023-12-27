
from django.urls import path
from ad import views

urlpatterns = [
    path('google/', views.google_ads),
]
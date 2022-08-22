
from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()

router.register('web', views.StartScrapeApiView, basename='scrapte')

urlpatterns = [
    path('', include(router.urls))
]
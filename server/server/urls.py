from django.contrib import admin
from rest_framework import permissions
from django.urls import path, include

from painting.views import *

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('painting.urls')),
]
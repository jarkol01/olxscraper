"""
URL configuration for olxscraper project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, include
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static
import os

from olxscraper.notifications.views import NotificationView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", NotificationView.as_view()),
    path("webpush/", include("webpush.urls")),
    path("", include("pwa.urls")),
    path(
        "serviceworker.js",
        serve,
        {
            "document_root": os.path.join(settings.BASE_DIR, "static"),
            "path": "serviceworker.js",
        },
    ),
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

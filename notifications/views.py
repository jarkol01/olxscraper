from django.shortcuts import render
from django.views.generic import TemplateView
from django.conf import settings


class NotificationView(TemplateView):
    template_name = "notification.html"

    def get_context_data(self, **kwargs):
        webpush = {"group": settings.DEFAULT_GROUP_NAME}
        context =  super().get_context_data(**kwargs)
        context["webpush"] = webpush

        return context
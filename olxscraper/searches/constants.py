from django.db import models
from django.utils.translation import gettext_lazy as _


class SiteChoices(models.TextChoices):
    OLX = "OLX", _("OLX")

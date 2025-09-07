from django.db import models
from django.utils.translation import gettext_lazy as _


class WebsiteChoices(models.TextChoices):
    OLX = "OLX", _("OLX")
    OTOMOTO = "OTOMOTO", _("OTOMOTO")
    KLEINANZEIGEN = "KLEINANZEIGEN", _("KLEINANZEIGEN")

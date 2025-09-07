from django.conf import settings


def environment_callback(request):
    """
    Callback function to display environment information in Unfold admin.
    """
    if settings.DEBUG:
        return ["Development", "warning"]
    else:
        return ["Production", "danger"]

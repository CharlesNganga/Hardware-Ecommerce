from django.conf import settings


def shop(request):
    # Replaced by the SiteSettings model in Phase 6.
    return {"shop_name": settings.SHOP_NAME}

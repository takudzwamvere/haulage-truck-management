from django.contrib.auth.models import User


def pending_users_count(request):
    """Add the count of pending (inactive) users to the template context for superusers."""
    if hasattr(request, 'user') and request.user.is_authenticated and request.user.is_superuser:
        count = User.objects.filter(is_active=False, is_superuser=False).count()
        return {'pending_users_count': count}
    return {'pending_users_count': 0}

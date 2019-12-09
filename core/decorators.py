from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def group_required(*group_names):
    def in_groups(u):
        if u.is_authenticated:
            if u.groups.filter(name__in=group_names).exists() | u.is_superuser:
                return True
            else:
                raise PermissionDenied
        return False
    return user_passes_test(in_groups)

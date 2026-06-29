from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


ADMIN_GROUP = "Admin"
ASSESSOR_GROUP = "Assessor"
ECD_GROUP = "Early Careers Definer"
ECAM_GROUP = "Early Careers Assessment Manager"


def user_group_names(user):
    if not user.is_authenticated:
        return set()

    return set(user.groups.values_list("name", flat=True))


def is_admin_user(user):
    return user.is_authenticated and (
        user.is_superuser or user_group_names(user).__contains__(ADMIN_GROUP)
    )


def has_any_group(user, allowed_groups):
    if is_admin_user(user):
        return True

    return bool(user_group_names(user).intersection(allowed_groups))


def nav_permissions(user):
    is_admin = is_admin_user(user)
    is_assessor = has_any_group(user, {ASSESSOR_GROUP})
    is_early_careers = has_any_group(user, {ECD_GROUP, ECAM_GROUP})

    return {
        "can_see_home": user.is_authenticated,
        "can_see_interview": user.is_authenticated,
        "can_see_applications": is_admin or is_early_careers,
        "can_see_create_pack": is_admin or is_assessor,
        "can_see_add_question": is_admin or is_assessor,
        "can_see_create_category": is_admin or is_assessor,
    }


def group_required(*allowed_groups):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if has_any_group(request.user, set(allowed_groups)):
                return view_func(request, *args, **kwargs)

            messages.error(request, "You do not have permission to access that page.")
            return redirect("home")

        return wrapped

    return decorator

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

ALLOWED_ROLES = {"admin","vendor"}

def user_can_manage(user) -> bool:
    return bool(
        getattr(user, "is_superuser", False)
        or getattr(user, "is_staff", False)
        or getattr(user, "role", None) in ALLOWED_ROLES
    )

def can_manage_required(view):
    @wraps(view)
    def _wrap(request, *a, **kw):
        if not request.user.is_authenticated:
            return redirect("login")
        if not user_can_manage(request.user):
            messages.error(request, "No tienes permisos para esta acción.")
            return redirect("dashboard")
        return view(request, *a, **kw)
    return _wrap

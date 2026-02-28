from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.urls import reverse_lazy



def _dashboard_for_user(user):


    if user.is_staff:
        return reverse_lazy("admin_dashboard")

    if user.is_seller:
           if user.is_verified_seller:
               return reverse_lazy("seller_profile")
          
           return reverse_lazy("user_seller")

    return reverse_lazy("home")


# ================================================
# SELLER REQUIRED DECORATOR
# ================================================

def seller_profile_required(view_func=None, login_url=None):

    login_url = login_url or reverse_lazy("login")
    apply_url = reverse_lazy("seller_registration")

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            user = request.user

            if not user.is_authenticated:
                return redirect(
                    f"{login_url}?{REDIRECT_FIELD_NAME}={request.get_full_path()}"
                )

    
            if not user.is_seller:
                return redirect(apply_url)

            return view_func(request, *args, **kwargs)

        return wrapper

    if view_func:
        return decorator(view_func)
    return decorator

def verified_seller_required(view_func=None,login_url=None):
    login_url = login_url or reverse_lazy("login")
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request,*args,**kwargs):
            user=request.user
            if not user.is_authenticated:
                return redirect (f"{login_url}?{REDIRECT_FIELD_NAME}={request.get_full_path()}"
                )
            if not user.is_seller:
                return redirect("seller_registration")
            if not user.is_verified_seller:
                return redirect(_dashboard_for_user(user))
            return view_func(request,*args, **kwargs)
        return wrapper
    if view_func:
        return decorator(view_func)
    return decorator

# ==============================================================================
# ADMIN REQUIRED DECORATOR
# ==============================================================================

def admin_required(view_func=None, login_url=None):
    """
    Allows only staff users (Admin).

    Checks:
    1. user.is_authenticated
    2. user.is_active
    3. user.is_staff
    """

    login_url = login_url or reverse_lazy("login")

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = request.user

            # 1️⃣ Not logged in
            if not user.is_authenticated:
                return redirect(
                    f"{login_url}?{REDIRECT_FIELD_NAME}={request.get_full_path()}"
                )

            # 2️⃣ Account disabled
            if not user.is_active:
                messages.error(request, "Your account has been deactivated.")
                return redirect(login_url)

            # 3️⃣ Not admin
            if not user.is_staff:
                messages.error(
                    request,
                    "You do not have permission to access this page."
                )
                return redirect(_dashboard_for_user(user))

            return view_func(request, *args, **kwargs)

        return wrapper

    if view_func:
        return decorator(view_func)
    return decorator



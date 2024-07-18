from django.shortcuts import redirect
from functools import wraps

def role_required(*required_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role not in required_roles:
                return redirect('profile')  # Redirect to a suitable page or show an error
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
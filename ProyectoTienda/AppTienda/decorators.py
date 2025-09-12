from django.http import HttpResponseNotFound
from django.shortcuts import render
from functools import wraps

def user_passes_test_404(test_func):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            return render(request, 'AppTienda/404.html', {})
        return _wrapped_view
    return decorator
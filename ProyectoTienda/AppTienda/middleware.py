from django.shortcuts import redirect

class RedirectAccountsLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/accounts/login/':
            return redirect('/tienda/login/')
        response = self.get_response(request)
        return response
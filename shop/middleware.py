from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

class AuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Check if the request path requires authentication and the user is authenticated
        if request.path.startswith('/api/orders/') and not request.user.is_authenticated:
            return JsonResponse({'detail': 'Authentication credentials were not provided.'}, status=401)
        return None

from .models import RequestLog, BlockedIP
from django.utils.timezone import now
from django.http import HttpResponseForbidden

class IPLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):        
        ip = self.get_client_ip(request)

        if BlockedIP.objects.filter(ip_address=ip).exists():
            return HttpResponseForbidden("Your IP has been blocked.")
        
        # Log the request
        RequestLog.objects.create(
            ip_address=ip,
            timestamp=now(),
            path=request.path
        )
        # Continue with request
        return self.get_response(request)

    def get_client_ip(self, request):
        """Retrieve IP from headers or remote addr"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

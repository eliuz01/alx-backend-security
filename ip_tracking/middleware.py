from .models import RequestLog, BlockedIP
from django.utils.timezone import now
from django.http import HttpResponseForbidden
from django.core.cache import cache
from ipware import get_client_ip
import requests

class IPLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip, _ = get_client_ip(request)

        if not ip:
            ip = "0.0.0.0"

        # 🔒 Check blacklist
        if BlockedIP.objects.filter(ip_address=ip).exists():
            return HttpResponseForbidden("Your IP has been blocked.")

        # 🌍 Try cached geolocation
        geo_data = cache.get(f"geo_{ip}")

        if not geo_data:
            try:
                response = requests.get(f"https://ipinfo.io/{ip}/json", timeout=3)
                data = response.json()
                geo_data = {
                    "country": data.get("country"),
                    "city": data.get("city"),
                }
                # Cache for 24 hours (86400 seconds)
                cache.set(f"geo_{ip}", geo_data, timeout=86400)
            except Exception:
                geo_data = {"country": None, "city": None}

        # ✅ Log the request
        RequestLog.objects.create(
            ip_address=ip,
            timestamp=now(),
            path=request.path,
            country=geo_data.get("country"),
            city=geo_data.get("city"),
        )

        return self.get_response(request)

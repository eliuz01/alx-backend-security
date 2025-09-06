from django.http import JsonResponse
from django.conf import settings
from django_ratelimit.decorators import ratelimit


# Anonymous users → 5/min
@ratelimit(key="ip", rate=settings.RATELIMIT_ANON, method="POST", block=True)
# Authenticated users → 10/min
@ratelimit(key="ip", rate=settings.RATELIMIT_AUTH, method="POST", block=True)
def login_view(request):
    if request.method == "POST":
        # Fake login logic for demo
        return JsonResponse({"message": "Login attempt"})
    return JsonResponse({"error": "Only POST allowed"}, status=405)

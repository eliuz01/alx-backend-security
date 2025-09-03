# ip_tracking/tasks.py
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import RequestLog, SuspiciousIP

SENSITIVE_PATHS = ["/admin", "/login"]

@shared_task
def detect_anomalies():
    one_hour_ago = timezone.now() - timedelta(hours=1)

    # 1. Flag IPs with more than 100 requests in the past hour
    from django.db.models import Count
    heavy_users = (
        RequestLog.objects.filter(timestamp__gte=one_hour_ago)
        .values("ip_address")
        .annotate(request_count=Count("id"))
        .filter(request_count__gt=100)
    )

    for entry in heavy_users:
        SuspiciousIP.objects.get_or_create(
            ip_address=entry["ip_address"],
            reason=f"Excessive requests: {entry['request_count']} in the last hour"
        )

    # 2. Flag IPs accessing sensitive paths
    suspicious_access = RequestLog.objects.filter(
        timestamp__gte=one_hour_ago,
        path__in=SENSITIVE_PATHS
    ).values("ip_address", "path")

    for entry in suspicious_access:
        SuspiciousIP.objects.get_or_create(
            ip_address=entry["ip_address"],
            reason=f"Accessed sensitive path: {entry['path']}"
        )

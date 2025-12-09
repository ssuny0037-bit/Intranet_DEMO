from datetime import date, timedelta
from django.urls import reverse
from .models import CompanySite

def expiration_alerts(request):
    today = date.today()
    soon = today + timedelta(days=30)

    alerts = []

    hosting = CompanySite.objects.filter(
        hosting_expire_at__isnull=False,
        hosting_expire_at__lte=soon
    )
    for site in hosting:
        alerts.append({
            "company": site.company.name,
            "type": "호스팅",
            "date": site.hosting_expire_at,
            "url": reverse("admin:core_company_change", args=[site.company.id]),
        })

    domain = CompanySite.objects.filter(
        domain_expire_at__isnull=False,
        domain_expire_at__lte=soon
    )
    for site in domain:
        alerts.append({
            "company": site.company.name,
            "type": "도메인",
            "date": site.domain_expire_at,
            "url": reverse("admin:core_company_change", args=[site.company.id]),
        })

    return {"expiration_alerts": alerts}

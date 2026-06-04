from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
import dns.resolver
import httpx

from .models import Domain
from .serializers import DomainSerializer
from apps.scans.models import Scan
from apps.scans.tasks import run_scan
from engine.ssrf_guard import validate_hostname


class DomainViewSet(viewsets.ModelViewSet):
    serializer_class = DomainSerializer

    def get_queryset(self):
        return Domain.objects.filter(owner=self.request.user)

    @action(detail=True, methods=["post"])
    def verify(self, request, pk=None):
        domain = self.get_object()
        if domain.is_verified:
            return Response({"detail": "Domain is already verified.", "verified": True})

        token = domain.verification_token
        verified = False

        if domain.verification_method == "dns_txt":
            try:
                answers = dns.resolver.resolve(f"_posturescan.{domain.hostname}", "TXT")
                for rdata in answers:
                    for string in rdata.strings:
                        if string.decode() == token:
                            verified = True
            except Exception:
                pass
        else:  # well_known
            try:
                resp = httpx.get(
                    f"https://{domain.hostname}/.well-known/posturescan-{token}",
                    timeout=10,
                    follow_redirects=True,
                )
                if resp.status_code == 200 and token in resp.text:
                    verified = True
            except Exception:
                pass

        if verified:
            domain.is_verified = True
            domain.verified_at = timezone.now()
            domain.save(update_fields=["is_verified", "verified_at"])
            return Response({"detail": "Domain verified successfully.", "verified": True})

        return Response(
            {
                "detail": "Verification failed. Check your DNS record or well-known file.",
                "verified": False,
                "dns_hint": f"Add TXT record → _posturescan.{domain.hostname}  =  {token}",
                "file_hint": f"Host file at https://{domain.hostname}/.well-known/posturescan-{token} containing the token.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=True, methods=["post"])
    def scan(self, request, pk=None):
        domain = self.get_object()
        if not domain.is_verified:
            return Response(
                {"detail": "Domain must be verified before scanning."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # SSRF pre-check before we even enqueue
        try:
            validate_hostname(domain.hostname)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        scan_obj = Scan.objects.create(domain=domain)
        run_scan.delay(scan_obj.pk)
        return Response(
            {"scan_id": scan_obj.pk, "status": scan_obj.status},
            status=status.HTTP_202_ACCEPTED,
        )

    @action(detail=True, methods=["get"])
    def history(self, request, pk=None):
        domain = self.get_object()
        scans = domain.scans.filter(status="completed").order_by("created_at").values(
            "id", "score", "grade", "created_at"
        )
        return Response(list(scans))

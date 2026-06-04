from celery import shared_task
from django.utils import timezone
import httpx

from .models import Scan, CheckResult
from engine.ssrf_guard import validate_hostname
from engine.tls import check_tls
from engine.headers import check_headers
from engine.cookies import check_cookies
from engine.redirects import check_redirects
from engine.grading import compute_grade


@shared_task(bind=True, max_retries=1, default_retry_delay=30)
def run_scan(self, scan_id: int):
    scan = Scan.objects.select_related("domain").get(pk=scan_id)
    domain = scan.domain

    if not domain.is_verified:
        scan.status = "failed"
        scan.error_message = "Domain not verified. Verify ownership before scanning."
        scan.save(update_fields=["status", "error_message"])
        return

    scan.status = "running"
    scan.started_at = timezone.now()
    scan.save(update_fields=["status", "started_at"])

    all_results = []
    try:
        # SSRF guard: confirm DNS resolves to a public IP
        validate_hostname(domain.hostname)

        target_url = f"https://{domain.hostname}"

        # 1. TLS checks
        all_results.extend(check_tls(domain.hostname))

        # 2. HTTP fetch — inspect headers and cookies
        response = httpx.get(
            target_url,
            follow_redirects=True,
            timeout=15,
            headers={"User-Agent": "PostureScanner/1.0"},
        )
        all_results.extend(check_headers(dict(response.headers)))

        set_cookies = [v for k, v in response.headers.multi_items() if k.lower() == "set-cookie"]
        all_results.extend(check_cookies(set_cookies))

        # 3. Open redirect probe
        all_results.extend(check_redirects(target_url))

        # 4. Grade everything
        grade_result = compute_grade(all_results)

        # 5. Persist all check results
        VALID_FIELDS = {f.name for f in CheckResult._meta.get_fields()}
        CheckResult.objects.bulk_create([
            CheckResult(scan=scan, **{k: v for k, v in r.items() if k in VALID_FIELDS})
            for r in all_results
        ])

        scan.score = grade_result["score"]
        scan.grade = grade_result["grade"]
        scan.status = "completed"
        scan.finished_at = timezone.now()
        scan.save(update_fields=["score", "grade", "status", "finished_at"])

        domain.last_scanned_at = timezone.now()
        domain.save(update_fields=["last_scanned_at"])

    except Exception as exc:
        scan.status = "failed"
        scan.error_message = str(exc)
        scan.finished_at = timezone.now()
        scan.save(update_fields=["status", "error_message", "finished_at"])
        try:
            raise self.retry(exc=exc)
        except Exception:
            pass

from django.db import models
from apps.domains.models import Domain


class Scan(models.Model):
    STATUS_CHOICES = [
        ("queued",    "Queued"),
        ("running",   "Running"),
        ("completed", "Completed"),
        ("failed",    "Failed"),
    ]
    GRADE_CHOICES = [(g, g) for g in ("A", "B", "C", "D", "F")]

    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, related_name="scans")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="queued")
    score = models.IntegerField(null=True, blank=True)
    grade = models.CharField(max_length=1, choices=GRADE_CHOICES, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Scan #{self.pk} — {self.domain.hostname} [{self.status}]"


class CheckResult(models.Model):
    STATUS_CHOICES = [("pass", "Pass"), ("warn", "Warn"), ("fail", "Fail"), ("info", "Info")]
    CATEGORY_CHOICES = [
        ("tls",       "TLS/SSL"),
        ("headers",   "HTTP Headers"),
        ("cookies",   "Cookies"),
        ("redirects", "Open Redirects"),
    ]
    SEVERITY_CHOICES = [
        ("critical", "Critical"), ("high", "High"),
        ("medium",   "Medium"),   ("low",  "Low"), ("info", "Info"),
    ]

    scan = models.ForeignKey(Scan, on_delete=models.CASCADE, related_name="check_results")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    check_key = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default="info")
    score_impact = models.IntegerField(default=0)
    observed_value = models.TextField(blank=True)
    expected_value = models.TextField(blank=True)
    remediation = models.TextField(blank=True)
    detail = models.JSONField(default=dict)   # PostgreSQL JSONB — stores raw evidence
    created_at = models.DateTimeField(auto_now_add=True)

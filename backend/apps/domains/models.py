import secrets
from django.db import models
from apps.accounts.models import User


class Domain(models.Model):
    VERIFICATION_CHOICES = [
        ("dns_txt", "DNS TXT Record"),
        ("well_known", "Well-Known File"),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="domains")
    hostname = models.CharField(max_length=253)
    is_verified = models.BooleanField(default=False)
    verification_method = models.CharField(
        max_length=20, choices=VERIFICATION_CHOICES, default="dns_txt"
    )
    verification_token = models.CharField(max_length=64, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    last_scanned_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("owner", "hostname")]

    def save(self, *args, **kwargs):
        if not self.verification_token:
            self.verification_token = secrets.token_hex(16)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.hostname

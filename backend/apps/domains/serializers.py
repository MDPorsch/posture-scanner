from rest_framework import serializers
from .models import Domain


class DomainSerializer(serializers.ModelSerializer):
    latest_grade = serializers.SerializerMethodField()

    class Meta:
        model = Domain
        fields = [
            "id", "hostname", "is_verified", "verification_method",
            "verification_token", "verified_at", "last_scanned_at",
            "created_at", "latest_grade",
        ]
        read_only_fields = [
            "is_verified", "verification_token", "verified_at",
            "last_scanned_at", "created_at",
        ]

    def get_latest_grade(self, obj):
        latest = obj.scans.filter(status="completed").order_by("-created_at").first()
        if latest:
            return {"score": latest.score, "grade": latest.grade}
        return None

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)

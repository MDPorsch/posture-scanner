from rest_framework import serializers
from .models import Scan, CheckResult


class CheckResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckResult
        exclude = ["scan"]


class ScanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scan
        fields = "__all__"


class ScanReportSerializer(serializers.ModelSerializer):
    check_results = CheckResultSerializer(many=True, read_only=True)

    class Meta:
        model = Scan
        fields = "__all__"

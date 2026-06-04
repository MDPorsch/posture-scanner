from rest_framework import generics
from .models import Scan
from .serializers import ScanSerializer, ScanReportSerializer


class ScanDetailView(generics.RetrieveAPIView):
    serializer_class = ScanSerializer

    def get_queryset(self):
        return Scan.objects.filter(domain__owner=self.request.user)


class ScanReportView(generics.RetrieveAPIView):
    serializer_class = ScanReportSerializer

    def get_queryset(self):
        return Scan.objects.filter(domain__owner=self.request.user)

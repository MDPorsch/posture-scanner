from django.urls import path
from .views import ScanDetailView, ScanReportView

urlpatterns = [
    path("scans/<int:pk>/",        ScanDetailView.as_view(),  name="scan-detail"),
    path("scans/<int:pk>/report/", ScanReportView.as_view(),  name="scan-report"),
]

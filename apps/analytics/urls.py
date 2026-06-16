from django.urls import path
from .views import DashboardView, GroqAnalysisView

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard-data'),
    path('ai-analysis/', GroqAnalysisView.as_view(), name='ai-analysis'),
]

from django.urls import path
from .views import IncomeListCreateView

urlpatterns = [
    path('', IncomeListCreateView.as_view(), name='income-list-create'),
]

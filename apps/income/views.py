from rest_framework import generics, permissions
from .models import Income
from .serializers import IncomeSerializer

class IncomeListCreateView(generics.ListCreateAPIView):
    serializer_class = IncomeSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        user = self.request.user if self.request.user.is_authenticated else None
        if not user:
            from django.contrib.auth import get_user_model
            user = get_user_model().objects.first()
        return Income.objects.filter(user=user)

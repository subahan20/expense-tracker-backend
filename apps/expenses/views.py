from rest_framework import generics, permissions
from .models import Expense
from .serializers import ExpenseSerializer

class ExpenseListCreateView(generics.ListCreateAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        user = self.request.user if self.request.user.is_authenticated else None
        if not user:
            from django.contrib.auth import get_user_model
            user = get_user_model().objects.first()
        return Expense.objects.filter(user=user)

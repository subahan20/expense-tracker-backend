from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from .models import Budget
from .serializers import BudgetSerializer

class BudgetView(generics.RetrieveUpdateAPIView, generics.CreateAPIView):
    serializer_class = BudgetSerializer
    # Allow any for now so frontend can hit it without auth token
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        # Fallback to first user if not authenticated
        user = self.request.user if self.request.user.is_authenticated else None
        if not user:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.first()
            
        try:
            return Budget.objects.get(user=user)
        except (Budget.DoesNotExist, AttributeError):
            return None

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

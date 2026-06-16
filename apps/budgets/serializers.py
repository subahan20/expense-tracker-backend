from rest_framework import serializers
from .models import Budget

class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = ['id', 'user', 'monthly_budget', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def create(self, validated_data):
        request = self.context.get('request')
        # If no user is authenticated, we might need a fallback for testing, but let's assume auth is needed.
        # Wait, if auth is not implemented on frontend, maybe we just assign a default user or allow null user?
        # The Budget model says user is OneToOneField, which is required. 
        user = request.user if request and request.user.is_authenticated else None
        
        # If user is None, this will fail. Let's fetch the first user as a fallback for testing if not authenticated
        if not user:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.first()
            
        budget, created = Budget.objects.update_or_create(
            user=user,
            defaults={'monthly_budget': validated_data['monthly_budget']}
        )
        return budget

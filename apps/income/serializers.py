from rest_framework import serializers
from .models import Income

class IncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Income
        fields = ['id', 'source', 'amount', 'income_date', 'created_at']

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None
        if not user:
            from django.contrib.auth import get_user_model
            user = get_user_model().objects.first()
        validated_data['user'] = user
        return super().create(validated_data)

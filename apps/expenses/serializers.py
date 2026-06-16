from rest_framework import serializers
from .models import Expense
from apps.categories.models import Category

class ExpenseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Expense
        fields = ['id', 'title', 'amount', 'expense_date', 'created_at', 'category_name']

    def create(self, validated_data):
        category_name = validated_data.pop('category_name', None)
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None
        if not user:
            from django.contrib.auth import get_user_model
            user = get_user_model().objects.first()
            
        validated_data['user'] = user

        if category_name:
            category, _ = Category.objects.get_or_create(name=category_name, user=user)
            validated_data['category'] = category

        return super().create(validated_data)

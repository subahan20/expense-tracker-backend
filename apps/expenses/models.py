import uuid
from django.db import models
from django.conf import settings
from apps.categories.models import Category
from django.utils import timezone

class Expense(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('CREDIT_CARD', 'Credit Card'),
        ('DEBIT_CARD', 'Debit Card'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('OTHER', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='expenses')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='expenses')
    title = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, default='CASH')
    expense_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-expense_date', '-created_at']

    def __str__(self):
        return f"{self.title} - {self.amount}"

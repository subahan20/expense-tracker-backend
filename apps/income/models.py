import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone

class Income(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='incomes')
    source = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    income_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-income_date', '-created_at']

    def __str__(self):
        return f"{self.source} - {self.amount}"

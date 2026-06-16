import uuid
from django.db import models
from django.conf import settings

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default="#000000")

    class Meta:
        verbose_name_plural = 'Categories'
        unique_together = ('user', 'name')

    def __str__(self):
        return f"{self.name} ({self.user.email})"

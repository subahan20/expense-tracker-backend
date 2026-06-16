from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/budgets/', include('apps.budgets.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
    path('api/income/', include('apps.income.urls')),
    path('api/expenses/', include('apps.expenses.urls')),
]

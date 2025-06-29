from django.db import models

class MerchantTransactionsModel(models.Model):
    user_id = models.IntegerField()
    transaction_id = models.CharField(max_length=255)
    amount = models.IntegerField()
    time = models.BigIntegerField()
    perform_time = models.BigIntegerField(null=True, blank=True)
    cancel_time = models.BigIntegerField(null=True, blank=True)
    state = models.IntegerField(default=1)
    reason = models.IntegerField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)  # Добавлено
    phone = models.CharField(max_length=30, null=True, blank=True)  # Добавлено
    created_at_ms = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
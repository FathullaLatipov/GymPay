from django.db import models

class MerchantTransactionsModel(models.Model):
    payment_id = models.CharField(max_length=100, unique=True)  # Новое, основной параметр account
    user_id = models.IntegerField()
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=30, null=True, blank=True)

    transaction_id = models.CharField(max_length=255)
    amount = models.IntegerField()
    time = models.BigIntegerField()
    perform_time = models.BigIntegerField(null=True, blank=True)
    cancel_time = models.BigIntegerField(null=True, blank=True)
    state = models.IntegerField(default=1)
    reason = models.IntegerField(null=True, blank=True)
    created_at_ms = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment #{self.payment_id} - User {self.user_id}"


    class Meta:
        verbose_name = 'Merchant'
        verbose_name_plural = 'Merchants'
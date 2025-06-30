from rest_framework import serializers
from payme.models import MerchantTransactionsModel


class GeneratePayLinkSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    amount = serializers.IntegerField()



class TestMyMerchantSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='_id')

    class Meta:
        model = MerchantTransactionsModel
        fields = ['_id', 'transaction_id', 'user_id', 'amount', 'time', 'perform_time','email', 'phone', 'payment_id',
                  'cancel_time', 'state', 'reason', 'created_at_ms', 'created_at', 'updated_at']

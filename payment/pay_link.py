# payment/pay_link.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from urllib.parse import urlencode
from config import settings

class GeneratePayLinkAPIView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            user_id = request.GET.get('user_id')
            email = request.GET.get('email', '')
            phone = request.GET.get('phone', '')
            amount = request.GET.get('amount')

            if not user_id or not amount:
                return Response(
                    {"error": "Missing required parameters"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            amount_in_tiyin = int(float(amount) * 100)

            merchant_id = settings.PAYME_ID

            params = {
                'merchant': merchant_id,
                'amount': amount_in_tiyin,
                'account[user_id]': str(user_id),
                'lang': 'ru'
            }

            if email:
                params['account[email]'] = email
            if phone:
                params['account[phone]'] = phone

            query_string = urlencode(params)
            payme_link = f'https://checkout.paycom.uz/{query_string}'

            return Response({'payme_link': payme_link}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

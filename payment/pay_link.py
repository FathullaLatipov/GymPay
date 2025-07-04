# payment/pay_link.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from urllib.parse import urlencode
from config import settings
from payment.models import MerchantTransactionsModel
import uuid
import time
import base64


# class GeneratePayLinkAPIView(APIView):
#     def get(self, request, *args, **kwargs):
#         try:
#             user_id = request.GET.get('user_id')
#             email = request.GET.get('email', '')
#             phone = request.GET.get('phone', '')
#             amount = request.GET.get('amount')
#
#             if not user_id or not amount:
#                 return Response(
#                     {"error": "Missing required parameters"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#
#             amount_in_tiyin = int(float(amount) * 100)
#
#             merchant_id = settings.PAYME_ID
#
#             params = {
#                 'merchant': merchant_id,
#                 'amount': amount_in_tiyin,
#                 'account[user_id]': str(user_id),
#                 'lang': 'ru'
#             }
#
#             if email:
#                 params['account[email]'] = email
#             if phone:
#                 params['account[phone]'] = phone
#
#             query_string = urlencode(params)
#             payme_link = f'https://checkout.paycom.uz/{query_string}'
#
#             return Response({'payme_link': payme_link}, status=status.HTTP_200_OK)
#
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class GeneratePayLinkAPIView(APIView):
#     def get(self, request, *args, **kwargs):
#         try:
#             user_id = request.GET.get('user_id')
#             email = request.GET.get('email', '')
#             phone = request.GET.get('phone', '')
#             amount = request.GET.get('amount')
#
#             if not user_id or not amount:
#                 return Response({"error": "Missing required parameters"}, status=400)
#
#             amount_in_tiyin = int(float(amount) * 100)
#             payment_id = str(uuid.uuid4())
#             now_ms = int(time.time() * 1000)
#
#             MerchantTransactionsModel.objects.create(
#                 user_id=user_id,
#                 transaction_id=payment_id,
#                 amount=amount_in_tiyin,
#                 time=now_ms,
#                 created_at_ms=now_ms,
#                 email=email,
#                 phone=phone
#             )
#
#             params = {
#                 'merchant': settings.PAYME_ID,
#                 'amount': amount_in_tiyin,
#                 'account[payment_id]': payment_id,
#                 'lang': 'ru'
#             }
#
#             payme_link = f'https://checkout.paycom.uz/{urlencode(params)}'
#             return Response({'payme_link': payme_link})
#
#         except Exception as e:
#             return Response({"error": str(e)}, status=500)

# class GeneratePayLinkAPIView(APIView):
#     def get(self, request, *args, **kwargs):
#         try:
#             user_id = request.GET.get('user_id')
#             email = request.GET.get('email', '')
#             phone = request.GET.get('phone', '')
#             amount = request.GET.get('amount')
#
#             if not user_id or not amount:
#                 return Response(
#                     {"error": "Missing required parameters"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#
#             # Сумма в тийинах
#             amount_in_tiyin = int(float(amount) * 100)
#
#             # Генерируем уникальный payment_id
#             payment_id = str(uuid.uuid4())
#
#             # Сохраняем транзакцию в БД
#             MerchantTransactionsModel.objects.create(
#                 user_id=user_id,
#                 amount=amount_in_tiyin,
#                 payment_id=payment_id,
#                 email=email,
#                 phone=phone,
#                 time=int(time.time() * 1000),
#                 created_at_ms=int(time.time() * 1000)
#             )
#
#             merchant_id = settings.PAYME_ID
#             # Формируем параметры для Payme
#             params = {
#                # 'merchant': settings.PAYME_ID,
#                 'amount': amount_in_tiyin,
#                 'account[payment_id]': payment_id,
#                 'lang': 'ru'
#             }
#
#             query_string = urlencode(params)
#            # payme_link = f'https://checkout.paycom.uz/?{query_string}'
#             payme_link = f'https://checkout.paycom.uz/{merchant_id}?{query_string}'
#
#             return Response({'payme_link': payme_link}, status=status.HTTP_200_OK)
#
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

            # Сумма в тийинах
            amount_in_tiyin = int(float(amount))

            # Генерируем уникальный payment_id
            payment_id = str(uuid.uuid4())

            # Сохраняем транзакцию в БД
            MerchantTransactionsModel.objects.create(
                user_id=user_id,
                amount=amount_in_tiyin,
                payment_id=payment_id,
                email=email,
                phone=phone,
                time=int(time.time() * 1000),
                created_at_ms=int(time.time() * 1000)
            )

            # merchant ID из настроек
            merchant_id = settings.PAYME_ID

            # Формируем строку параметров в формате key=value через `;`
            raw_params = f"m={merchant_id};ac.payment_id={payment_id};a={amount_in_tiyin};l=ru"

            # Кодируем в base64
            encoded_params = base64.b64encode(raw_params.encode()).decode()

            # Финальная ссылка на оплату
            payme_link = f"https://checkout.paycom.uz/{encoded_params}"

            return Response({'payme_link': payme_link}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# paymeuz/call_back.py

import requests
# from django.conf import settings
# from payme.views import MerchantAPIView
#
#
# class PaymeCallBackAPIView(MerchantAPIView):
#     def create_transaction(self, user_id, action, *args, **kwargs):
#         print(f"[CREATE] user_id: {user_id}, data: {action}")
#
#     def perform_transaction(self, user_id, action, *args, **kwargs):
#         print(f"[PERFORM] user_id: {user_id}, data: {action}")
#         self.send_to_getcourse(user_id, action.amount)
#
#     def cancel_transaction(self, user_id, action, *args, **kwargs):
#         print(f"[CANCEL] user_id: {user_id}, data: {action}")
#
#     def send_to_getcourse(self, user_id, amount):
#         try:
#             response = requests.post("https://fitpackcourse.getcourse.ru/pl/api/payments", data={
#                 "user": {
#                     "id": user_id
#                 },
#                 "amount": amount,
#                 "system": "Payme",
#                 "comment": "Оплата через Payme",
#                 "key": settings.GETCOURSE_API_KEY
#             })
#
#             print("[GETCOURSE RESPONSE]", response.status_code, response.text)
#         except Exception as e:
#             print("[ERROR GETCOURSE]", str(e))


import requests
from payment.models import MerchantTransactionsModel
from payme.views import PaymeWebHookAPIView
from config import settings


class PaymeCallbackView(PaymeWebHookAPIView):

    def handle_create_transaction(self, params, *args, **kwargs):
        try:
            account = params.get("account", {})
            user_id = account.get("user_id")
            email = account.get("email")
            phone = account.get("phone")
            transaction_id = params.get("id")
            amount = params.get("amount")
            time = params.get("time")
            created_at_ms = time

            # Проверка на дубликат (можно по transaction_id)
            if MerchantTransactionsModel.objects.filter(transaction_id=transaction_id).exists():
                print("[CREATE] Transaction already exists")
                return

            MerchantTransactionsModel.objects.create(
                user_id=user_id,
                transaction_id=transaction_id,
                amount=amount,
                time=time,
                created_at_ms=created_at_ms,
                email=email,
                phone=phone
            )
            print("[CREATE] Transaction saved")
        except Exception as e:
            print("[CREATE TRANSACTION ERROR]", str(e))

    def handle_successfully_payment(self, params, result, *args, **kwargs):
        print("[PAYME CALLBACK] Transaction performed. Sending to GetCourse")

        try:
            account = params.get("account", {})
            user_id = account.get("user_id")
            amount = params.get("amount")

            response = requests.post("https://fitpackcourse.getcourse.ru/pl/api/payments", data={
                "user": {
                    "id": user_id
                },
                "amount": amount,
                "system": "Payme",
                "comment": "Оплата через Payme",
                "key": settings.GETCOURSE_API_KEY
            })

            print("[GETCOURSE RESPONSE]", response.status_code, response.text)
        except Exception as e:
            print("[ERROR SENDING TO GETCOURSE]", str(e))

    def handle_cancel_transaction(self, params, transaction, *args, **kwargs):
        print("[CANCEL] Transaction canceled:", transaction.transaction_id)

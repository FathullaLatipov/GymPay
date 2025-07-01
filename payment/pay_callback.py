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

#
# class PaymeCallbackView(PaymeWebHookAPIView):
#
#     def handle_create_transaction(self, params, *args, **kwargs):
#         try:
#             account = params.get("account", {})
#             user_id = account.get("user_id")
#             email = account.get("email")
#             phone = account.get("phone")
#             transaction_id = params.get("id")
#             amount = params.get("amount")
#             time = params.get("time")
#             created_at_ms = time
#
#             # Проверка на дубликат (можно по transaction_id)
#             if MerchantTransactionsModel.objects.filter(transaction_id=transaction_id).exists():
#                 print("[CREATE] Transaction already exists")
#                 return
#
#             MerchantTransactionsModel.objects.create(
#                 user_id=user_id,
#                 transaction_id=transaction_id,
#                 amount=amount,
#                 time=time,
#                 created_at_ms=created_at_ms,
#                 email=email,
#                 phone=phone
#             )
#             print("[CREATE] Transaction saved")
#         except Exception as e:
#             print("[CREATE TRANSACTION ERROR]", str(e))
#
#     def handle_successfully_payment(self, params, result, *args, **kwargs):
#         print("[PAYME CALLBACK] Transaction performed. Sending to GetCourse")
#
#         try:
#             account = params.get("account", {})
#             user_id = account.get("user_id")
#             amount = params.get("amount")
#
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
#             print("[ERROR SENDING TO GETCOURSE]", str(e))
#
#     def handle_cancel_transaction(self, params, transaction, *args, **kwargs):
#         print("[CANCEL] Transaction canceled:", transaction.transaction_id)

# class PaymeCallbackView(PaymeWebHookAPIView):
#
#     def handle_create_transaction(self, params, *args, **kwargs):
#         try:
#             payment_id = params['account'].get('payment_id')
#             if not payment_id:
#                 print("[CREATE] Missing payment_id")
#                 return
#
#             transaction = MerchantTransactionsModel.objects.get(transaction_id=payment_id)
#             print(f"[CREATE] Found transaction {transaction.transaction_id}")
#         except MerchantTransactionsModel.DoesNotExist:
#             print("[CREATE ERROR] Transaction not found")
#
#     def handle_successfully_payment(self, params, result, *args, **kwargs):
#         try:
#             payment_id = params['account'].get('payment_id')
#             transaction = MerchantTransactionsModel.objects.get(transaction_id=payment_id)
#
#             response = requests.post("https://fitpackcourse.getcourse.ru/pl/api/payments", data={
#                 "user": {"id": transaction.user_id},
#                 "amount": transaction.amount,
#                 "system": "Payme",
#                 "comment": "Оплата через Payme",
#                 "key": settings.GETCOURSE_API_KEY
#             })
#
#             print("[GETCOURSE RESPONSE]", response.status_code, response.text)
#         except Exception as e:
#             print("[ERROR SEND TO GETCOURSE]", str(e))
#
#     def handle_cancel_transaction(self, params, transaction, *args, **kwargs):
#         print("[CANCEL] Transaction canceled:", transaction.transaction_id)

class PaymeCallbackView(PaymeWebHookAPIView):

    def handle_create_transaction(self, params, *args, **kwargs):
        try:
            payment_id = params['account'].get('payment_id')
            if not payment_id:
                print("[CREATE] ❌ Missing payment_id")
                return

            # Получаем сумму и другие данные
            transaction_id = params.get('id')
            time = params.get('time')
            amount = params.get('amount')

            # Получаем транзакцию по payment_id
            transaction = MerchantTransactionsModel.objects.get(payment_id=payment_id)

            # Обновляем данные
            transaction.transaction_id = transaction_id
            transaction.time = time
            transaction.amount = amount
            transaction.save()

            print(f"[CREATE ✅] Transaction updated: {transaction_id}")

        except MerchantTransactionsModel.DoesNotExist:
            print("[CREATE ❌] Transaction with payment_id not found")

        except Exception as e:
            print("[CREATE ❌ ERROR]", str(e))

    def check_perform_transaction(self, params):
        try:
            payment_id = params['account'].get('payment_id')
            amount = params['amount']

            if not payment_id:
                return self.error_response(
                    code=-31050,
                    message="Missing account.payment_id"
                )

            transaction = MerchantTransactionsModel.objects.get(payment_id=payment_id)

            if int(transaction.amount) != int(amount):
                return self.error_response(
                    code=-31001,
                    message=f"Invalid amount. Expected: {transaction.amount}, received: {amount}"
                )

            return {
                "result": {
                    "allow": True,
                    "additional": {
                        "user_id": str(transaction.user_id),
                        "email": transaction.email or "",
                        "phone": transaction.phone or ""
                    }
                }
            }

        except MerchantTransactionsModel.DoesNotExist:
            return self.error_response(
                code=-31050,
                message="Account does not exist"
            )

        except Exception as e:
            print("[CHECK PERFORM ERROR]", str(e))
            return self.error_response(
                code=-32400,
                message="Internal error"
            )

        except MerchantTransactionsModel.DoesNotExist:
            return self.error_response(
                code=-31050,
                message="Account does not exist"
            )

        except Exception as e:
            print("[CHECK PERFORM ERROR]", str(e))
            return self.error_response(
                code=-32400,
                message="Internal error"
            )

    def handle_successfully_payment(self, params, result, *args, **kwargs):
        try:
            payment_id = params['account'].get('payment_id')
            if not payment_id:
                print("[PERFORM ❌] Missing payment_id")
                return

            # Получаем транзакцию
            transaction = MerchantTransactionsModel.objects.get(payment_id=payment_id)

            # Отправка в GetCourse
            response = requests.post("https://fitpackcourse.getcourse.ru/pl/api/payments", data={
                "user": {"id": transaction.user_id},
                "amount": transaction.amount,
                "system": "Payme",
                "comment": "Оплата через Payme",
                "key": settings.GETCOURSE_API_KEY
            })

            print("[PERFORM ✅] Sent to GetCourse")
            print("[GETCOURSE RESPONSE]", response.status_code, response.text)

            return {
                "result": {
                    "perform_time": transaction.time,
                    "transaction": transaction.transaction_id,
                    "state": 1,  # выполнено
                    "payment_id": transaction.phone
                }
            }

        except MerchantTransactionsModel.DoesNotExist:
            print("[PERFORM ❌] Transaction not found")

        except Exception as e:
            print("[PERFORM ❌ ERROR]", str(e))

    def handle_cancel_transaction(self, params, transaction, *args, **kwargs):
        print("[CANCEL] ❌ Transaction canceled:", transaction.transaction_id)
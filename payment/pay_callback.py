# paymeuz/call_back.py
import json
import time

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
import logging
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
import os

logger = logging.getLogger(__name__)

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

            transaction_id = params.get('id')
            time = params.get('time')
            payme_amount = int(params.get('amount'))  # тийины

            transaction = MerchantTransactionsModel.objects.get(payment_id=payment_id)

            # ✅ Просто сравниваем, без умножения
            expected_amount = int(transaction.amount)  # в тийинах

            if expected_amount != payme_amount:
                return {
                    "error": {
                        "code": -31001,
                        "message": {
                            "uz": "Noto'g'ri summa",
                            "ru": "Неверная сумма",
                            "en": "Incorrect amount"
                        },
                        "data": f"Invalid amount. Expected: {expected_amount}, received: {payme_amount}"
                    }
                }

            # Всё хорошо — обновляем
            transaction.transaction_id = transaction_id
            transaction.time = time
            transaction.save()

            print(f"[CREATE ✅] Transaction updated: {transaction_id}")

        except MerchantTransactionsModel.DoesNotExist:
            print("[CREATE ❌] Transaction with payment_id not found")

        except Exception as e:
            print("[CREATE ❌ ERROR]", str(e))

    def check_perform_transaction(self, params):
        try:
            payment_id = params['account'].get('payment_id')
            amount = int(params['amount'])  # тийины

            if not payment_id:
                return {
                    "error": {
                        "code": -31050,
                        "message": {
                            "uz": "Hisob topilmadi",
                            "ru": "Счёт не найден",
                            "en": "Account not found"
                        },
                        "data": "Missing payment_id"
                    }
                }

            transaction = MerchantTransactionsModel.objects.get(payment_id=payment_id)

            # Приводим сумму из базы к тийинам для сравнения
            expected_amount = int(transaction.amount) * 100  # сумма в тийинах

            if expected_amount != amount:
                return {
                    "error": {
                        "code": -31001,
                        "message": {
                            "uz": "Noto'g'ri summa",
                            "ru": "Неверная сумма",
                            "en": "Incorrect amount"
                        },
                        "data": f"Expected: {expected_amount}, received: {amount}"
                    }
                }

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
            return {
                "error": {
                    "code": -31050,
                    "message": {
                        "uz": "Hisob topilmadi",
                        "ru": "Счёт не найден",
                        "en": "Account not found"
                    },
                    "data": f"payment_id={payment_id}"
                }
            }

        except Exception as e:
            print("[CHECK PERFORM ERROR]", str(e))
            return {
                "error": {
                    "code": -32400,
                    "message": {
                        "uz": "Ichki xatolik",
                        "ru": "Внутренняя ошибка",
                        "en": "Internal error"
                    },
                    "data": str(e)
                }
            }

    def handle_successfully_payment(self, params, result, *args, **kwargs):
        try:
            logger.debug(f"▶️ handle_successfully_payment called with params={params}")

            # 🛡️ Безопасно получаем payment_id
            account_data = params.get('account', {})
            if not isinstance(account_data, dict):
                logger.error(f"[PERFORM ❌] account не является словарём: {account_data}")
                return

            payment_id = account_data.get('payment_id')
            if not payment_id:
                logger.error("[PERFORM ❌] payment_id отсутствует в params['account']")
                return

            # 📦 Получаем транзакцию
            transaction = MerchantTransactionsModel.objects.get(payment_id=payment_id)

            # 💰 Определяем offer_code по сумме (в тийинах)
            amount = int(transaction.amount)
            if amount == 2000:
                offer_code = "3941295"  # тестовый или льготный
            elif amount == 1999000:
                offer_code = "3941675"
            else:
                logger.warning(f"[PERFORM ⚠️] Неизвестная сумма платежа: {amount}")
                return

            # 📤 Отправляем запрос в GetCourse
            response = requests.post(
                "https://fitpackcourse.getcourse.ru/pl/api/deals",
                data={
                    "user[email]": transaction.email,
                    "user[phone]": transaction.phone,
                    "deal[status]": "Оплачен",
                    "deal[offer_code]": offer_code,
                    "deal[created_at]": transaction.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    "system": "Payme",
                    "key": settings.GETCOURSE_API_KEY
                }
            )

            # ✅ Проверка ответа от GetCourse
            if response.status_code != 200:
                logger.error(f"[PERFORM ❌] Ошибка от GetCourse: {response.status_code} | {response.text}")
                return

            # 💾 Сохраняем успешное выполнение
            transaction.perform_time = int(time.time() * 1000)
            transaction.state = 1
            transaction.save()

            logger.info(f"[PERFORM ✅] Доступ выдан: {offer_code} → {transaction.email}")

            return {
                "result": {
                    "perform_time": transaction.perform_time,
                    "transaction": transaction.transaction_id,
                    "state": 1,
                    "payment_id": transaction.phone
                }
            }

        except MerchantTransactionsModel.DoesNotExist:
            logger.error(f"[PERFORM ❌] Транзакция не найдена: payment_id={payment_id}")

        except Exception as e:
            logger.exception(f"[PERFORM ❌ ERROR] Неожиданная ошибка: {str(e)}")

    def handle_cancel_transaction(self, params, transaction, *args, **kwargs):
        print("[CANCEL] ❌ Transaction canceled:", transaction.transaction_id)


@method_decorator(csrf_exempt, name='dispatch')
class GetCourseWebhookView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        try:
            data = request.data.dict() if hasattr(request.data, 'dict') else request.data
            logger.info(f"[GETCOURSE WEBHOOK] Received: {data}")

            action = data.get("action")
            email = data.get("user[email]") or data.get("email")
            amount = data.get("payment[amount]") or data.get("amount")
            status_ = data.get("payment[status]") or data.get("status")
            method = data.get("payment[method]") or data.get("method")

            logger.info(f"[GETCOURSE INFO] Email: {email}, Amount: {amount}, Status: {status_}, Method: {method}")

            # Пример: отметка оплаты
            if action == "payment.created" and email:
                transaction = MerchantTransactionsModel.objects.filter(email=email).last()
                if transaction:
                    transaction.state = 1  # Выполнено
                    transaction.perform_time = int(time.time() * 1000)
                    transaction.save()
                    logger.info(f"[GETCOURSE ✅] Transaction marked as paid: {transaction.id}")

            return Response({"status": "ok"}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception("[GETCOURSE WEBHOOK ❌ ERROR]")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
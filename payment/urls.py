# paymeuz/urls.py
from django.urls import path

from payment.pay_link import GeneratePayLinkAPIView
from payment.pay_callback import PaymeCallbackView, GetCourseWebhookView

urlpatterns = [
    path('pay-link/', GeneratePayLinkAPIView.as_view(), name='generate-pay-link'),
    path('payme/callback/', PaymeCallbackView.as_view(), name='payme-callback'),
    path("getcourse/webhook/", GetCourseWebhookView.as_view(), name="getcourse-webhook"),
]

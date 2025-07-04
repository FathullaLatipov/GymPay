from django.contrib import admin
from django.urls import path,  include

from payment.pay_callback import PaymeCallbackView
from .yasg import urlpatterns as doc_urls
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
urlpatterns = [
    path('admin/', admin.site.urls),
    path('payments/merchant/', include('payment.urls')),
]


urlpatterns += doc_urls
from . import views
from django.urls import path, include

urlpatterns = [
    path('signin', views.sign_in),
    path('signup', views.sign_up),
    path('get-public-token', views.initialize_link),
    path('exchange-token', views.exchange_token),
    path('transactions', views.fetch_accounts),
    path('fire-webhooks', views.fire_webhook),
    path('webhook', views.webhook),
    path('update-webhook-url', views.update_webhook_url)
]

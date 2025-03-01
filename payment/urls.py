from django.urls import path
from . import views


app_name = 'payment'

urlpatterns = [
   
   
    
    path('invoice/<int:payment_id>/', views.download_invoice, name='download_invoice'),
    path('checkout/<uuid:transaction_id>/', views.checkout, name='checkout'),
    path('subscription_needed/', views.subscription_needed, name='subscription_needed'),
    path('subscribe/<int:plan_id>/', views.subscribe_to_plan, name='subscribe_to_plan'),
    path('success/<str:transaction_id>/', views.subscription_success, name='subscription_success'),
    #path('success/', views.subscription_success, name="subscription_success"),
    path('failure/', views.failure, name="failure"),
    path('trial_expired/', views.trial_expired, name='trial_expired'),
    path('check_active_subscription/', views.check_active_subscription, name='check_active_subscription'),
    path('invoice/<str:transaction_id>/', views.view_invoice, name='view_invoice'),
    path('invoice/download/<str:transaction_id>/', views.download_invoice, name='download_invoice'),
    
    #path("pay/<int:amount>/<str:description>/", views.create_payment, name="create_payment"),
     # Affiliate payment URL
    path('pay-affiliate/<int:commission_id>/', views.pay_affiliate_commission, name='pay_affiliate_commission'),
    # Existing paths...
    path('pay-all-pending-commissions/<int:affiliate_id>/', views.pay_all_pending_affiliate_commissions, name='pay_all_pending_affiliate_commissions'),
    path("webhook/", views.webhook, name="webhook"),
]


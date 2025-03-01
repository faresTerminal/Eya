from django.urls import path
from . import views




urlpatterns = [
    path('become-affiliate/', views.become_affiliate, name='become_affiliate'),
    path('dashboard/', views.affiliate_dashboard, name='affiliate_dashboard'),
    path('ref/<str:affiliate_code>/', views.track_referral, name='track_referral'),
    path('buyer_dashboard/', views.buyer_commission_dashboard, name='buyer_commission_dashboard'),
    path('buyer_dashboard/<int:affiliate_id>/', views.affiliate_commission_detail, name='affiliate_commission_detail'),
    path('analytics/', views.affiliate_analytics, name='affiliate_analytics'),
    path('success/<int:commission_id>/', views.affiliate_payment_success, name='affiliate_payment_success'),  # ✅ Single Payment
    path('success/', views.affiliate_payment_success, name='affiliate_payment_bulk_success'),  # ✅ Bulk Payment
   
]




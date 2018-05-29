from django.contrib import admin
from django.urls import path, include

from . import views

app_name = 'kdv'
urlpatterns = [
    path('', views.LedgerView.as_view(), name='ledger'),
    path('add_record/', views.AddRecordView.as_view(), name='add_record'),
    path('buy/<int:barcode>/', views.BuyProductView.as_view(), name='buy_product'),
    path('challenge/<int:pk>/', views.ChallengeTransactionView.as_view(), name='challenge_transaction'),
    path('unchallenge/<int:pk>/', views.UnChallengeTransactionView.as_view(), name='unchallenge_transaction'),
    path('return/<int:pk>/', views.ReturnTransactionView.as_view(), name='return_transaction'),
    path('revoke/<int:pk>/', views.RevokeRecordView.as_view(), name='revoke_record'),
    path('add_transaction/', views.AddTransactionView.as_view(), name='add_transaction'),
    path('productlist/', views.ProductListView.as_view(), name='productlist'),
    path('account/', views.AccountView.as_view(), name='account'),
]
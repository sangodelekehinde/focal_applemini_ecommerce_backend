from django.urls import path
from .views import CheckoutView, OrderListView, VerifyPaymentView

urlpatterns = [
    path("checkout/", CheckoutView.as_view()),                              # POST: order + payment link
    path("payments/verify/<str:reference>/", VerifyPaymentView.as_view()),  # GET: confirm payment
    path("orders/", OrderListView.as_view()),                               # GET: order history
]
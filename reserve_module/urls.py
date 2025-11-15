from django.urls import path
from reserve_module import views

urlpatterns = [
    path('', views.ReserveRoomView.as_view(), name='reserve_room_page'),
    path('add-room-to-reserve/', views.add_room_to_reserve, name='add_room_to_reserve_page'),
    path('remove-room-type-reserve', views.remove_room_type_reserve, name='remove_room_type_reserve_page'),
    path('cancel-reserve/', views.CancelReserveView.as_view(), name='cancel_reserve_page'),
    path('request-payment/', views.send_request_payment, name='request-payment'),
    path('verify-payment/', views.verify_payment, name='verify-payment'),
    path('payment/', views.demo_payment, name='demo_room_payment_page'),
    path('success-payment/', views.success_payment, name='success_payment_room_page'),
    path('cancel-payment/', views.cancel_payment, name='cancel_payment_room_page'),
]

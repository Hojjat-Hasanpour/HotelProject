from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.TourListView.as_view(), name='tours_page'),
    path('reserve-tour/', views.TourBookingCreateView.as_view(), name='tour_reserve_page'),
    path('cancel-reserve-tour/', views.CancelTourBookingFormView.as_view(), name='cancel_tour_reserve_page'),
    re_path(r'tour/(?P<slug>[-\w]+)/', views.TourDetailView.as_view(), name='tour_detail_page'),
    path('payment/', views.payment, name='payment_tour_page'),
    path('success-payment/', views.success_payment, name='success_payment_tour_page'),
    path('cancel-payment/', views.cancel_payment, name='cancel_payment_tour_page'),
    # path('tour/<slug:slug>/', views.tour, name='tourId'), # Edit For Persian
]

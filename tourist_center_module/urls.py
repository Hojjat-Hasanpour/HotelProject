from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.TouristCenterListView.as_view(), name='tourist_center_page'),
    re_path(r'(?P<slug>[-\w]+)/', views.TouristCenterDetailView.as_view(), name='tourist_detail_page'),
]

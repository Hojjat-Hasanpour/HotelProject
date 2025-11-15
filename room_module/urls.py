from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.RoomsView.as_view(), name='rooms_page'),
    re_path(r'room/(?P<slug>[-\w]+)/', views.RoomDetailView.as_view(), name='room_detail_page'),
    # path('<slug:slug>', views.RoomDetailView, name='room_detail_page'),
]

from django.shortcuts import render

from django.views.generic import TemplateView, DetailView
from room_module.models import RoomCategory, RoomType, RoomImage


class RoomsView(TemplateView):
    template_name = 'room_module/rooms.html'

    def get_context_data(self, **kwargs):
        context = super(RoomsView, self).get_context_data()
        room_category: RoomCategory = RoomCategory.objects.filter(is_active=True).prefetch_related('roomtype_set')
        context['room_category'] = room_category

        return context


class RoomDetailView(DetailView):
    model = RoomType
    template_name = 'room_module/room_detail.html'
    context_object_name = 'room'

    def get_queryset(self):
        query = super(RoomDetailView, self).get_queryset()
        query = query.filter(is_active=True)
        return query

    def get_context_data(self, **kwargs):
        context = super(RoomDetailView, self).get_context_data()
        # room: Room = kwargs.get('object')
        current_room = self.object
        room_images: RoomImage = RoomImage.objects.filter(room_category=current_room.category)
        context['room_images'] = room_images
        return context

from django.shortcuts import render
from django.views.generic import TemplateView, ListView

from hotel.models import Advantages, Introduction
from room_module.models import RoomImage, RoomType
from service_module.models import Services
from site_module.models import SiteSetting, Slider, HomeImageReservation
from tour_module.models import Tour
from utils.convertor import group_list


class HomeView(TemplateView):
    template_name = 'hotel/index.html'

    def get_context_data(self, **kwargs):
        setting: SiteSetting = SiteSetting.objects.filter(site_name__iexact='هتل سجاد').first()
        slider: Slider = Slider.objects.filter(is_active=True)
        image_reserve: HomeImageReservation = HomeImageReservation.objects.filter(is_active=True).first()
        room_types: RoomType = RoomType.objects.filter(is_active=True)
        tours = Tour.objects.filter(is_active=True).order_by('?')[:3]
        services = Services.objects.filter(is_active=True)[:6]
        context = super().get_context_data(**kwargs)
        context['site_setting'] = setting
        context['slider'] = slider
        context['image_reserve'] = image_reserve
        context['room_types'] = room_types
        context['tours'] = tours
        context['services'] = services
        return context


def site_header_component(request):
    setting: SiteSetting = SiteSetting.objects.filter(site_name__iexact='هتل سجاد').first()
    context = {
        'site_setting': setting
    }
    return render(request, 'shared/site_header_component.html', context)


def site_footer_component(request):
    setting: SiteSetting = SiteSetting.objects.filter(site_name__iexact='هتل سجاد').first()
    services: Services = Services.objects.filter(is_active=True)[:4]
    context = {
        'site_setting': setting,
        'services': services
    }
    return render(request, 'shared/site_footer_component.html', context)


class AdvantagesView(TemplateView):
    template_name = 'hotel/advantage.html'

    def get_context_data(self, **kwargs):
        advantages: Advantages = Advantages.objects.filter(is_active=True)
        context = super().get_context_data(**kwargs)
        context['advantages'] = advantages
        return context


class IntroductionView(TemplateView):
    template_name = 'hotel/introduction.html'

    def get_context_data(self, **kwargs):
        intros: Introduction = Introduction.objects.filter(is_active=True).order_by('order')
        context = super().get_context_data(**kwargs)
        context['introductions'] = intros
        return context


class GalleryListView(ListView):
    template_name = 'hotel/gallery.html'
    model = RoomImage
    context_object_name = 'room_images'
    paginate_by = 12

    # def get_queryset(self):
    #     query = super(GalleryListView, self).get_queryset()
    #     query = query.filter(is_active=True)
    #     return query

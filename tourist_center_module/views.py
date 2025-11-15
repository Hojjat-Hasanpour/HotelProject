from django.shortcuts import render
from tourist_center_module.models import TouristCenter
from django.views.generic import TemplateView, ListView, DetailView


# class TouristCenterView(TemplateView):
#     template_name = 'tourist_center_module/tourist_center.html'


class TouristCenterListView(ListView):
    model = TouristCenter
    paginate_by = 6
    template_name = 'tourist_center_module/tourist_center.html'
    context_object_name = 'tourist_center'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(TouristCenterListView, self).get_context_data()
        return context

    def get_queryset(self):
        query = super(TouristCenterListView, self).get_queryset()
        query = query.filter(is_active=True)

        return query


class TouristCenterDetailView(DetailView):
    model = TouristCenter
    template_name = 'tourist_center_module/tourist_detail.html'
    context_object_name = 'tourist'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(TouristCenterDetailView, self).get_context_data()
        return context

    def get_queryset(self):
        query = super(TouristCenterDetailView, self).get_queryset()
        query = query.filter(is_active=True)
        return query

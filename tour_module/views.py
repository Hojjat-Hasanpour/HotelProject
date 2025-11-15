import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView, FormView

from tour_module.forms import TourBookingModelForm, CancelTourBookingModelForm
from tour_module.models import Tour, TourBooking


class TourListView(ListView):
    model = Tour
    template_name = 'tour_module/tours.html'
    context_object_name = 'tours'
    paginate_by = 8

    def get_queryset(self):
        query = super(TourListView, self).get_queryset()
        query = query.filter(is_active=True)
        return query


class TourDetailView(DetailView):
    model = Tour
    template_name = 'tour_module/tour_detail.html'
    context_object_name = 'tour'

    def get_queryset(self):
        query = super(TourDetailView, self).get_queryset()
        query = query.filter(is_active=True)
        return query

    def get_context_data(self, **kwargs):
        context = super(TourDetailView, self).get_context_data()
        # room: Room = kwargs.get('object')

        return context


class TourBookingCreateView(CreateView):
    form_class = TourBookingModelForm
    model = TourBooking
    template_name = 'tour_module/reserve_tour.html'
    success_url = '/tours/payment/'

    def get_form_kwargs(self):
        kwargs = super(TourBookingCreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        obj = form.save(commit=False)
        remaining_capacity = TourBooking.objects.filter(tour_id=obj.tour.id, is_delete=False).aggregate(
            reserve_sum=Sum('number'))
        if remaining_capacity['reserve_sum'] is None:
            remaining_capacity['reserve_sum'] = 0
        if obj.number > (obj.tour.capacity - remaining_capacity['reserve_sum']):
            messages.error(self.request, 'تور ظرفیت ندارد. لطفا تور دیگری را انتخاب فرمایید')
            return super(TourBookingCreateView, self).form_invalid(form)

        obj.user = self.request.user
        obj.save()
        return super(TourBookingCreateView, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'خطا در عملیات.')
        return super(TourBookingCreateView, self).form_invalid(form)


class CancelTourBookingFormView(FormView):
    form_class = CancelTourBookingModelForm
    model = TourBooking
    template_name = 'tour_module/cancel_reserve_tour.html'
    success_url = '/tours/cancel-reserve-tour/'

    def get_form_kwargs(self):
        kwargs = super(CancelTourBookingFormView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        obj = form.save(commit=False)
        selected_tour_booking = TourBooking.objects.filter(user_id=self.request.user.id, tour_id=obj.tour.id,
                                                           is_delete=False, is_paid=True)
        selected_tour_booking.update(is_delete=True)
        messages.success(self.request, 'تور مورد نظر با موفقیت لغو شد، جهت مبلغ تور به امور مالی مراجعه فرمایید.')
        # obj.user = self.request.user
        # obj.save()
        return super(CancelTourBookingFormView, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'خطا در عملیات.')
        return super(CancelTourBookingFormView, self).form_invalid(form)


@login_required
def payment(request):
    try:
        selected_tour_booking = TourBooking.objects.get(user_id=request.user.id, is_paid=False, is_delete=False)
        total_price = selected_tour_booking.calculate_total_price()
    except:
        selected_tour_booking = None
        total_price = 0
    context = {
        'selected_tour_booking': selected_tour_booking,
        'total_price': total_price,
    }

    return render(request, 'tour_module/payment.html', context)


@login_required
def success_payment(request):
    try:
        tourbooking_id = int(request.GET.get('tour_id'))
    except ValueError:
        return JsonResponse({
            'status': 'invalid_tour_id',
            'message': 'شماره آیدی تور معتبر نیست.',
        })
    try:
        selected_tour = TourBooking.objects.get(id=tourbooking_id, user_id=request.user.id, is_delete=False,
                                                is_paid=False)
    except:
        # messages.error(request, 'تور مورد نظر وجود ندارد')
        # return render(request, 'tour_module/reserve_tour.html')
        return JsonResponse({
            'status': 'not_tour_found',
            'message': 'تور مورد نظر وجود ندارد.',
        })

    selected_tour.is_paid = True
    selected_tour.payment_date = datetime.date.today()
    selected_tour.save()
    # messages.success(request, 'پرداخت شما موفقیت آمیز بود.')
    # return redirect(reverse('tour_reserve_page'))
    return JsonResponse({
        'status': 'success',
        'message': 'پرداخت شما موفقیت آمیز بود.',
    })


@login_required
def cancel_payment(request):
    try:
        tourbooking_id = int(request.GET.get('tour_id'))
    except ValueError:
        return JsonResponse({
            'status': 'invalid_tour_id',
            'message': 'تور مورد نظر وجود ندارد.',
        })
    try:
        selected_tour = TourBooking.objects.get(
            id=tourbooking_id, is_paid=False, is_delete=False, user=request.user).delete()
    except:
        return JsonResponse({
            'status': 'not_tour_found',
            'message': 'تور مورد نظر وجود ندارد.',
        })
    return JsonResponse({
        'status': 'failed',
        'message': 'کاربر از پرداخت مبلغ ممانعت کرد.',
    })

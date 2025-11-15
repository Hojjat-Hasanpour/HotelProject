import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Case, When, Q, Sum, IntegerField
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator

from django.views import View

from account_module.forms import RoomBookingForm
from reserve_module.models import RoomBooking, RoomBookingDetail
from room_module.models import RoomType, RoomNumber
from tour_module.models import TourBooking

from django.shortcuts import redirect
import requests
import json

MERCHANT = 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX'
ZP_API_REQUEST = "https://api.zarinpal.com/pg/v4/payment/request.json"
ZP_API_VERIFY = "https://api.zarinpal.com/pg/v4/payment/verify.json"
ZP_API_STARTPAY = "https://www.zarinpal.com/pg/StartPay/{authority}"
amount = 11000  # Rial / Required
description = "نهایی کردن خرید"  # Required
email = ''  # Optional
mobile = ''  # Optional
# Important: need to edit for really server.
CallbackURL = 'http://localhost:8000/reserve/verify-payment/'


@method_decorator(login_required, name='dispatch')
class ReserveRoomView(View):
    def post(self, request):
        reserve_form = RoomBookingForm(request.POST)
        if reserve_form.is_valid():
            start_date_form = reserve_form.cleaned_data.get('start_date')
            end_date_form = reserve_form.cleaned_data.get('end_date')
            capacity_form = reserve_form.cleaned_data.get('capacity')

            RoomBooking.objects.filter(is_paid=False, user_id=request.user.id).exclude(start_date=start_date_form,
                                                                                       end_date=end_date_form,
                                                                                       capacity=capacity_form).delete()

            current_room_booking, created = RoomBooking.objects.get_or_create(is_paid=False, user_id=request.user.id,
                                                                              start_date=start_date_form,
                                                                              end_date=end_date_form,
                                                                              capacity=capacity_form)

            context = {  # not necessary
                'current_room_booking': current_room_booking,
            }
            return render(request, 'reserve_module/reserve_room.html', context)

        room_booking_user = RoomBooking.objects.filter(user_id=request.user.id, is_paid=True, is_delete=False) \
            .prefetch_related('roombookingdetail_set')
        tour_booking_user = TourBooking.objects.filter(user_id=request.user.id, is_delete=False)
        context = {
            'room_booking_form': reserve_form,
            'room_booking_user': room_booking_user,
            'tour_booking_user': tour_booking_user
        }
        return render(request, 'account_module/dashboard.html', context)


@login_required
def add_room_to_reserve(request):
    try:
        room_id = int(request.GET.get('room_id'))
        count = int(request.GET.get('count'))
    except ValueError:
        return JsonResponse({
            'status': 'invalid_count_room_id',
            'title': 'خطا در عملیات.',
            'message': 'شماره اتاق یا تعداد وارد شده معتبر نمی باشد.',
        })

    if count < 1:
        return JsonResponse({
            'status': 'invalid_count',
            'title': 'خطا در عملیات.',
            'message': 'تعداد وارد شده معتبر نمی باشد.',
        })
    current_list = RoomBooking.objects.get(is_paid=False, user_id=request.user.id)

    # delete_count, delete_dict = RoomBookingDetail.objects.filter(room_booking_id=current_list.id,
    #                                                              room_number__room_type_id=room_id).delete()

    rooms = RoomNumber.objects.filter(room_type_id=room_id).exclude(
        roombookingdetail__room_booking__start_date__lte=current_list.end_date,
        roombookingdetail__room_booking__end_date__gte=current_list.start_date
    )[:count]

    if rooms is not None:
        for sub_room in rooms:
            new_detail = RoomBookingDetail(room_booking_id=current_list.id, room_number=sub_room, final_price=0)
            new_detail.save()

        type_rooms: RoomType = RoomType.objects.filter(is_active=True, roomnumber__is_active=True).annotate(
            room_count=Count(Case(
                When(~Q(roomnumber__roombookingdetail__room_booking__start_date__lte=current_list.end_date), then=1),
                When(~Q(roomnumber__roombookingdetail__room_booking__end_date__gte=current_list.start_date), then=1))))

        reserve_room_types: RoomType = RoomType.objects.filter(
            roomnumber__roombookingdetail__room_booking=current_list).distinct()

        accept_capacity = RoomType.objects.filter(roomnumber__roombookingdetail__room_booking_id=current_list.id) \
            .aggregate(accept_sum=Sum('capacity', output_field=IntegerField()),
                       total_price=Sum('price', output_field=IntegerField()))

        if accept_capacity['accept_sum'] is None:
            accept_capacity['accept_sum'] = 0

        if accept_capacity['total_price'] is None:
            accept_capacity['total_price'] = 0

        context = {
            'accept_capacity': accept_capacity,
            'type_rooms': type_rooms,
            'reserve_room_types': reserve_room_types,
            'current_roombooking': current_list,
            'status': 'success',
            'title': 'عملیات موفقیت آمیز.',
            'message': 'اتاق با موفقیت به لیست رزرو افزوده شد.'
        }
        return render(request, 'reserve_module/includes/reserve_room_partial.html', context)

    else:
        return JsonResponse({
            'status': 'not_found'
        })


@login_required
def reserve_room_component(request):
    current_roombooking: RoomBooking = RoomBooking.objects.get(user_id=request.user, is_paid=False)

    type_rooms: RoomType = RoomType.objects.filter(is_active=True, roomnumber__is_active=True).annotate(
        room_count=Count(Case(
            When(~Q(roomnumber__roombookingdetail__room_booking__start_date__lte=current_roombooking.end_date), then=1),
            When(~Q(roomnumber__roombookingdetail__room_booking__end_date__gte=current_roombooking.start_date),
                 then=1))))

    reserve_room_types: RoomType = RoomType.objects.filter(
        roomnumber__roombookingdetail__room_booking=current_roombooking).distinct()
    accept_capacity = RoomType.objects.filter(roomnumber__roombookingdetail__room_booking_id=current_roombooking.id) \
        .aggregate(accept_sum=Sum('capacity', output_field=IntegerField()),
                   total_price=Sum('price', output_field=IntegerField()))
    if accept_capacity['accept_sum'] is None:
        accept_capacity['accept_sum'] = 0

    if accept_capacity['total_price'] is None:
        accept_capacity['total_price'] = 0
    context = {
        'current_roombooking': current_roombooking,
        'accept_capacity': accept_capacity,
        'type_rooms': type_rooms,
        'reserve_room_types': reserve_room_types,
    }
    return render(request, 'reserve_module/includes/reserve_room_partial.html', context)


@login_required
def remove_room_type_reserve(request):
    try:
        room_type_id = int(request.GET.get('room_type_id'))
    except ValueError:
        return JsonResponse({
            'status': 'room_type_id_not_an_number',
            'message': 'شماره وارد شده صحیح نیست.'
        })

    current_roombooking: RoomBooking = RoomBooking.objects.filter(user_id=request.user.id, is_paid=False).first()
    deleted_count, deleted_dict = RoomBookingDetail.objects.filter(
        room_booking__is_paid=False,
        room_booking__user_id=request.user.id,
        room_number__room_type_id=room_type_id).delete()

    if deleted_count == 0:
        return JsonResponse({
            'status': 'detail_not_found',
            'message': 'جزئیات یافت نشد.'
        })

    type_rooms: RoomType = RoomType.objects.filter(is_active=True, roomnumber__is_active=True).annotate(
        room_count=Count(Case(
            When(~Q(roomnumber__roombookingdetail__room_booking__start_date__lte=current_roombooking.end_date), then=1),
            When(~Q(roomnumber__roombookingdetail__room_booking__end_date__gte=current_roombooking.start_date),
                 then=1))))

    reserve_room_types: RoomType = RoomType.objects.filter(
        roomnumber__roombookingdetail__room_booking=current_roombooking).distinct()

    accept_capacity = RoomType.objects.filter(roomnumber__roombookingdetail__room_booking_id=current_roombooking.id) \
        .aggregate(accept_sum=Sum('capacity', output_field=IntegerField()),
                   total_price=Sum('price', output_field=IntegerField()))
    if accept_capacity['accept_sum'] is None:
        accept_capacity['accept_sum'] = 0

    if accept_capacity['total_price'] is None:
        accept_capacity['total_price'] = 0

    context = {
        'accept_capacity': accept_capacity,
        'type_rooms': type_rooms,
        'current_roombooking': current_roombooking,
        'reserve_room_types': reserve_room_types,
        'title': 'عملیات موفقیت آمیز بود.',
        'message': 'اتاق با موفقیت از لیست رزرو حذف شد.',
        'status': 'success'
    }
    return render(request, 'reserve_module/includes/reserve_room_partial.html', context)


@method_decorator(login_required, name='dispatch')
class CancelReserveView(View):
    def get(self, request):
        # form = CancelReserveForm()
        # form.fields['selected_roombooking'].queryset = RoomBooking.objects.filter(user_id=request.user.id,
        #                                                                           start_date__gt=datetime.date.today(),
        #                                                                           is_delete=False)
        room_bookings: RoomBooking = RoomBooking.objects.filter(user_id=request.user.id,
                                                                start_date__gt=datetime.date.today(), is_delete=False)
        return render(request, 'reserve_module/cancel_reserve.html', {'room_bookings': room_bookings})

    def post(self, request):
        id_room_booking = request.POST.get('selected_roombooking')
        confirm_check = request.POST.get('confirm')
        deleted_roombooking = RoomBooking.objects.filter(user_id=request.user.id, id=id_room_booking, is_delete=False)
        if deleted_roombooking and confirm_check == 'on':
            deleted_roombooking.update(is_delete=True)
            messages.success(self.request,
                             'لیست مورد نظر با موفقیت حذف شد جهت پیگیری مبلغ به امورمالی هتل مراجعه فرمایید.')

        else:
            messages.error(self.request, 'لیست مورد نظر یافت نشد. خطایی در عملیات رخ داده است.')
        # if cancel_reserve_form.is_valid():
        #     # print(cancel_reserve_form.fields['selected_roombooking'])
        #     RoomBooking.objects.get(user_id=request.user.id, )

        #     RoomBooking.objects.filter(user_id=request.user.id, )
        #     print(cancel_reserve_form.fields['selected_roombooking'])
        #     selected_reserve: RoomBooking = RoomBooking.objects.get(id=)
        #     selected_reserve.update(is_delete=True)
        remaining_room_booking: RoomBooking = RoomBooking.objects.filter(user_id=request.user.id, is_delete=False)

        return render(request, 'reserve_module/cancel_reserve.html', {'room_bookings': remaining_room_booking})


@login_required
def send_request_payment(request):
    current_booking = RoomBooking.objects.get(is_paid=False, user_id=request.user.id, is_delete=False)
    total_price = current_booking.calculate_total_price()
    if total_price == 0:
        return redirect(reverse('reserve_room_page'))

    req_data = {
        "merchant_id": MERCHANT,
        "amount": total_price,  # Rial Important
        "callback_url": CallbackURL,
        "description": description,
        # "metadata": {"mobile": mobile, "email": email}
    }
    req_header = {"accept": "application/json", "content-type": "application/json"}
    req = requests.post(url=ZP_API_REQUEST, data=json.dumps(req_data), headers=req_header)
    authority = req.json()['data']['authority']
    if len(req.json()['errors']) == 0:
        return redirect(ZP_API_STARTPAY.format(authority=authority))
    else:
        e_code = req.json()['errors']['code']
        e_message = req.json()['errors']['message']
        return HttpResponse(f"Error code: {e_code}, Error Message: {e_message}")


@login_required
def verify_payment(request):
    current_booking = RoomBooking.objects.get(is_paid=False, user_id=request.user.id, is_delete=False)
    total_price = current_booking.calculate_total_price()
    t_authority = request.GET['Authority']
    if request.GET.get('Status') == 'OK':
        req_header = {"accept": "application/json", "content-type": "application/json'"}
        req_data = {
            "merchant_id": MERCHANT,
            "amount": total_price,  # Rial Important
            "authority": t_authority
        }
        req = requests.post(url=ZP_API_VERIFY, data=json.dumps(req_data), headers=req_header)
        if len(req.json()['errors']) == 0:
            t_status = req.json()['data']['code']
            if t_status == 100:
                current_booking.is_paid = True
                current_booking.payment_date = datetime.date.today()
                current_booking.save()
                ref_str = req.json()['data']['ref_id']
                return render(request, 'reserve_module/payment_result.html', {
                    'success': f'تراکنش شما با کد پیگیری {ref_str} با موفقیت انجام شد.'
                })
                # return HttpResponse('Transaction success.\nRefID: ' + str(req.json()['data']['ref_id']))
            elif t_status == 101:
                return render(request, 'reserve_module/payment_result.html', {
                    'info': 'این تراکنش قبلا ثبت شده است.'
                })
                # return HttpResponse('Transaction submitted : ' + str(req.json()['data']['message']))
            else:
                return render(request, 'reserve_module/payment_result.html', {
                    'error': str(req.json()['data']['message'])
                })
                # return HttpResponse('Transaction failed.\nStatus: ' + str(req.json()['data']['message']))
        else:
            e_code = req.json()['errors']['code']
            e_message = req.json()['errors']['message']
            # return HttpResponse(f"Error code: {e_code}, Error Message: {e_message}")
            return render(request, 'reserve_module/payment_result.html', {
                'error': f'کد خطا {e_code}: {e_message}'
            })
    else:
        # return HttpResponse('Transaction failed or canceled by user')
        return render(request, 'reserve_module/payment_result.html', {
            'error': 'پرداخت با خطا مواجه شد / کاربر از پرداخت ممانعت کرد.'
        })


@login_required
def demo_payment(request):
    try:
        # start_date greater than today
        current_room_booking = RoomBooking.objects.get(user_id=request.user.id, is_paid=False, is_delete=False)
        # current_room_booking_detail =
        total_price = current_room_booking.calculate_total_price()
    except:
        current_room_booking = None
        total_price = 0
    context = {
        'current_room_booking': current_room_booking,
        'total_price': total_price,
    }

    return render(request, 'reserve_module/demo_payment.html', context)


@login_required
def success_payment(request):
    try:
        room_booking_id = int(request.GET.get('room_booking_id'))
    except ValueError:
        return JsonResponse({
            'status': 'invalid_room_id',
            'message': 'شماره آیدی اتاق معتبر نیست.',
        })
    try:
        current_room_booking = RoomBooking.objects.get(id=room_booking_id, user_id=request.user.id, is_delete=False,
                                                       is_paid=False)
    except:
        return JsonResponse({
            'status': 'not_room_found',
            'message': 'اتاق مورد نظر وجود ندارد.',
        })

    current_room_booking.is_paid = True
    current_room_booking.payment_date = datetime.date.today()
    current_room_booking.save()
    return JsonResponse({
        'status': 'success',
        'message': 'پرداخت شما موفقیت آمیز بود.',
    })


@login_required
def cancel_payment(request):
    try:
        room_booking_id = int(request.GET.get('room_booking_id'))
    except ValueError:
        return JsonResponse({
            'status': 'invalid_room_id',
            'message': 'اتاق مورد نظر وجود ندارد.',
        })
    try:
        selected_tour = TourBooking.objects.get(
            id=room_booking_id, is_paid=False, is_delete=False, user=request.user).delete()
    except:
        return JsonResponse({
            'status': 'not_room_found',
            'message': 'اتاق مورد نظر وجود ندارد.',
        })
    return JsonResponse({
        'status': 'failed',
        'message': 'کاربر از پرداخت مبلغ ممانعت کرد.',
    })

from django.db import models
from jalali_date import date2jalali

from account_module.models import User
from room_module.models import RoomNumber


class RoomBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='کاربر')

    start_date = models.DateField(verbose_name='تاریخ شروع')
    end_date = models.DateField(verbose_name='تاریخ پایان')
    amount = models.IntegerField(verbose_name='تعداد روزها')
    capacity = models.IntegerField(verbose_name='ظرفیت')
    is_paid = models.BooleanField(default=False, verbose_name='پرداخت شده')
    payment_date = models.DateField(null=True, blank=True, verbose_name='تاریخ پرداخت')
    is_delete = models.BooleanField(default=False, verbose_name='حذف شده')

    class Meta:
        verbose_name = 'لیست رزرو'
        verbose_name_plural = 'لیست های رزرو'

    def __str__(self):
        return f'{self.user} - تاریخ شروع {date2jalali(self.start_date).strftime("%Y/%m/%d")} - تاریخ پایان {date2jalali(self.end_date).strftime("%Y/%m/%d")}'

    def save(self, *arg, **kwargs):
        self.amount = (self.end_date - self.start_date).days
        super(RoomBooking, self).save()

    def calculate_total_price(self):
        total_amount = 0
        if self.is_paid:
            for room_booking_detail in self.roombookingdetail_set.all():
                total_amount += room_booking_detail.final_price
        else:
            for room_booking_detail in self.roombookingdetail_set.all():
                total_amount += room_booking_detail.room_number.room_type.price
        return total_amount


class RoomBookingDetail(models.Model):
    room_booking = models.ForeignKey(RoomBooking, on_delete=models.CASCADE, verbose_name='لیست رزرو')
    room_number = models.ForeignKey(RoomNumber, on_delete=models.CASCADE, verbose_name='شماره اتاق رزرو')
    final_price = models.IntegerField(null=True, blank=True, verbose_name='قیمت نهایی')

    class Meta:
        verbose_name = 'جزئیات لیست رزرو'
        verbose_name_plural = 'جزئیات لیست های رزرو'

    def __str__(self):
        return f'{self.room_booking}'

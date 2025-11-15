from django.contrib import admin
from jalali_date import datetime2jalali, date2jalali
from jalali_date.admin import ModelAdminJalaliMixin

from . import models


# Register your models here.


class TourAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    readonly_fields = ['slug']
    list_display = ['name', 'capacity', 'is_active', 'get_start_date_jalali', 'get_end_date_jalali', 'day_number',
                    'price', 'slug']
    list_editable = ['is_active', 'price']

    def get_start_date_jalali(self, obj):
        return date2jalali(obj.start_date).strftime('%Y/%m/%d')

    def get_end_date_jalali(self, obj):
        return date2jalali(obj.end_date).strftime('%Y/%m/%d')

    get_start_date_jalali.short_description = 'تاریخ شروع'
    get_start_date_jalali.admin_order_field = 'start_date'
    get_end_date_jalali.short_description = 'تاریخ پایان'
    get_end_date_jalali.admin_order_field = 'end_date'


class TourBookingAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    def get_created_jalali(self, obj):
        return datetime2jalali(obj.created).strftime('%y/%m/%d _ %H:%M:%S')


admin.site.register(models.Tour, TourAdmin)
admin.site.register(models.TourBooking, TourBookingAdmin)

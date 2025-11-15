from django.contrib import admin
from . import models

# Register your models here.
from jalali_date import datetime2jalali
from jalali_date.admin import ModelAdminJalaliMixin


class RoomBookingAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    def get_created_jalali(self, obj):
        return datetime2jalali(obj.created).strftime('%y/%m/%d _ %H:%M:%S')


class RoomBookingDetailAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    def get_created_jalali(self, obj):
        return datetime2jalali(obj.created).strftime('%y/%m/%d _ %H:%M:%S')


admin.site.register(models.RoomBooking, RoomBookingAdmin)
admin.site.register(models.RoomBookingDetail, RoomBookingDetailAdmin)

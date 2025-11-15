from django.contrib import admin
from django.utils.html import format_html
from jalali_date import datetime2jalali
from jalali_date.admin import ModelAdminJalaliMixin

from . import models


# Register your models here.


class RoomTypeAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    # prepopulated_fields = {
    #     'slug': ['name'],
    # }
    readonly_fields = ['slug']

    list_display = ['name', 'category', 'is_active', 'slug']
    list_editable = ['is_active']
    list_filter = ['category']

    def get_created_jalali(self, obj):
        return datetime2jalali(obj.created).strftime('%y/%m/%d _ %H:%M:%S')


class RoomCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_editable = ['is_active']


class RoomNumberAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    list_display = ['number', 'room_type', 'is_active']
    list_editable = ['is_active']

    def get_created_jalali(self, obj):
        return datetime2jalali(obj.created).strftime('%y/%m/%d _ %H:%M:%S')


class RoomImageAdmin(admin.ModelAdmin):
    list_display = ['name_image', 'image_tag']

    def image_tag(self, obj):
        return format_html('<img src="{}" width=100px height=100px />'.format(obj.image.url))

    image_tag.short_description = 'تصویر'


admin.site.register(models.RoomNumber, RoomNumberAdmin)
admin.site.register(models.RoomType, RoomTypeAdmin)
admin.site.register(models.RoomCategory, RoomCategoryAdmin)
admin.site.register(models.RoomImage, RoomImageAdmin)

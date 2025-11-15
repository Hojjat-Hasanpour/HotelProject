from django.contrib import admin
from . import models


# Register your models here.


class TouristCenterAdmin(admin.ModelAdmin):
    readonly_fields = ['slug']
    list_display = ['name', 'is_active', 'slug']
    list_editable = ['is_active']


admin.site.register(models.TouristCenter, TouristCenterAdmin)

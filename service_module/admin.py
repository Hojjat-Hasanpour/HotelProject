from django.contrib import admin
from .models import Services
# Register your models here.


class ServicesAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'slug']
    list_editable = ['is_active']
    readonly_fields = ['slug']


admin.site.register(Services, ServicesAdmin)

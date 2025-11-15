from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from jalali_date import date2jalali

from account_module.models import User
from datetime import date


# Create your models here.


class Tour(models.Model):
    name = models.CharField(max_length=50, verbose_name='نام')
    price = models.IntegerField(verbose_name='قیمت')
    day_number = models.IntegerField(null=False, blank=True, verbose_name='تعداد روز های تور', editable=False)
    capacity = models.IntegerField(verbose_name='ظرفیت')
    start_date = models.DateField(verbose_name='روز شروع')
    end_date = models.DateField(verbose_name='روز پایان')
    description = models.TextField(verbose_name='توضیحات')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    image = models.ImageField(upload_to='images/tour', verbose_name='عکس')
    slug = models.SlugField(max_length=150, db_index=True, allow_unicode=True, null=False, editable=False,
                            verbose_name='عنوان در url', blank=True)

    # day_number = (datetime(end_day)-datetime(start_day)).days

    class Meta:
        verbose_name = 'تور'
        verbose_name_plural = 'تورها'

    def get_absolute_url(self):
        return reverse('tour_detail_page', args=[self.slug])

    def get_jalali_start_day(self):
        return date2jalali(self.start_date)

    def get_jalali_end_day(self):
        return date2jalali(self.end_date)

    def create_unique_slug(self, tour_id, room_slug):
        find_room = Tour.objects.filter(slug__iexact=room_slug)
        if find_room.exists():
            room_slug = f'{room_slug}-{tour_id}'
            self.create_unique_slug(tour_id, room_slug)

        return room_slug

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name, allow_unicode=True)
        self.slug = self.create_unique_slug(self.id, self.slug)
        self.day_number = (self.end_date - self.start_date).days
        #         (datetime(self.end_date.year, self.end_date.month, self.end_date.day) - datetime(self.start_date.year,
        #                                                                                      self.start_date.month,
        #                                                                                     self.start_date.day)).days

        super().save(*args, **kwargs)

    def clean(self):
        super(Tour, self).clean()
        # if datetime(self.start_day.year,
        #             self.start_day.month,
        #             self.start_day.day) < datetime.today() or datetime(self.start_day.year, self.start_day.month,
        #                                                                self.start_day.day) < datetime.today():
        #     raise ValidationError('تاریخ های وارد شده صحیح نیستند.')

        if self.start_date < date.today():
            raise ValidationError({'start_date': 'تاریخ شروع باید از امروز بیشتر باشد.'})

        if self.end_date < self.start_date:
            raise ValidationError({'end_date': 'تاریخ پایان باید از تاریخ شروع بیشتر باشد.'})

        if self.end_date < date.today():
            raise ValidationError({'end_date': 'تاریخ پایان باید از امروز بیشتر باشد.'})

    def __str__(self):
        return f'{self.name}'


class TourBooking(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, verbose_name='تور رزرو')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='کاربر')
    number = models.IntegerField(verbose_name='تعداد افراد')
    is_delete = models.BooleanField(default=False, verbose_name='حذف شده')
    is_paid = models.BooleanField(default=False, verbose_name='پرداخت شده')
    payment_date = models.DateField(null=True, blank=True, verbose_name='تاریخ پرداخت')

    class Meta:
        verbose_name = 'رزرو تور'
        verbose_name_plural = 'لیست تورهای رزرو'

    def __str__(self):
        return f'{self.user} - {self.tour}'

    def calculate_total_price(self):
        return self.number * self.tour.price

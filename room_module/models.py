from django.db import models
from django.urls import reverse

from account_module.models import User
from django.utils.text import slugify


class RoomCategory(models.Model):
    name = models.CharField(max_length=50, db_index=True, verbose_name='نام')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    is_delete = models.BooleanField(default=False, verbose_name='حذف شده')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'دسته بندی'
        verbose_name_plural = 'دسته بندی ها'


class RoomType(models.Model):
    name = models.CharField(max_length=50, verbose_name='نام')
    category = models.ForeignKey(RoomCategory, on_delete=models.CASCADE, verbose_name='دسته بندی')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    description = models.TextField(verbose_name='توضیحات')

    capacity = models.IntegerField(verbose_name='ظرفیت')
    slug = models.SlugField(max_length=150, null=False, db_index=True, allow_unicode=True, editable=False,
                            verbose_name='عنوان در url')
    price = models.IntegerField(verbose_name='قیمت نوع اتاق', blank=True, null=True)  # TODO remove blank, null
    main_image = models.ImageField(upload_to='images/rooms', null=False, blank=True, verbose_name='عکس اصلی اتاق')

    class Meta:
        verbose_name = 'نوع اتاق'
        verbose_name_plural = 'انواع اتاق ها'

    def __str__(self):
        return f'{self.name}'

    def get_absolute_url(self):
        return reverse('room_detail_page', args=[self.slug])

    def create_unique_slug(self, room_no, room_slug):
        find_room = RoomType.objects.filter(slug__iexact=room_slug)
        if find_room.exists():
            room_slug = f'{room_slug}-{room_no}'
            self.create_unique_slug(room_no, room_slug)

        return room_slug

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name, allow_unicode=True)
        self.slug = self.create_unique_slug(self.id, self.slug)
        super().save(*args, **kwargs)


class RoomNumber(models.Model):
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, verbose_name='نوع اتاق')
    number = models.IntegerField(unique=True, verbose_name='شماره اتاق')
    is_active = models.BooleanField(default=True, verbose_name='فعال')

    def __str__(self):
        return f'{self.room_type} - {self.number}'

    class Meta:
        verbose_name = 'شماره اتاق'
        verbose_name_plural = 'شماره اتاق ها'


class RoomImage(models.Model):
    name_image = models.CharField(max_length=50, verbose_name='نام عکس')
    image = models.ImageField(upload_to='images/rooms', verbose_name='عکس')
    room_category = models.ForeignKey(RoomCategory, on_delete=models.CASCADE, verbose_name='نام دسته بندی اتاق')

    def __str__(self):
        return f'{self.name_image} - {self.room_category.name}'

    class Meta:
        verbose_name = 'عکس اتاق'
        verbose_name_plural = 'عکس های اتاق'

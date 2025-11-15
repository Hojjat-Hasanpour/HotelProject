from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class TouristCenter(models.Model):
    name = models.CharField(max_length=50, verbose_name='نام')
    description = models.TextField(verbose_name='توضیحات')
    image = models.ImageField(upload_to='images/tourist_center', verbose_name='عکس تور')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    slug = models.SlugField(max_length=150, db_index=True, allow_unicode=True, null=False, blank=True,
                            verbose_name='عنوان در url')

    class Meta:
        verbose_name = 'مرکز گردشگری'
        verbose_name_plural = 'مراکز گردشگری'

    def get_absolute_url(self):
        return reverse('tourist_detail_page', args=[self.slug])

    def create_unique_slug(self, tourist_id, tourist_slug):
        find_tourist = TouristCenter.objects.filter(slug__iexact=tourist_slug)
        if find_tourist.exists():
            tourist_slug = f'{tourist_slug}-{tourist_id}'
            self.create_unique_slug(tourist_id, tourist_slug)

        return tourist_slug

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name, allow_unicode=True)
        self.slug = self.create_unique_slug(self.id, self.slug)
        super(TouristCenter, self).save()

    def __str__(self):
        return self.name

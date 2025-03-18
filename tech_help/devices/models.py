from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.conf import settings
from django.urls import reverse
from unidecode import unidecode  # добавим для корректной транслитерации

class DeviceCategory(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(unique=True, blank=True)
    
    class Meta:
        verbose_name = 'Категория устройств'
        verbose_name_plural = 'Категории устройств'
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.name))
        super().save(*args, **kwargs)


class SpecificationCategory(models.Model):
    """Категория характеристик (например, 'Дизайн', 'Экран', 'Процессор')"""
    name = models.CharField(max_length=100, verbose_name='Название')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок отображения')

    class Meta:
        verbose_name = 'Категория характеристик'
        verbose_name_plural = 'Категории характеристик'
        ordering = ['order']

    def __str__(self):
        return self.name

class SpecificationField(models.Model):
    """Поле характеристики (например, 'Вес', 'Толщина', 'Высота')"""
    category = models.ForeignKey(
        SpecificationCategory, 
        on_delete=models.CASCADE,
        related_name='fields',
        verbose_name='Категория'
    )
    name = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(
        blank=True, 
        verbose_name='Описание',
        help_text='Объяснение характеристики'
    )
    unit = models.CharField(
        max_length=20, 
        blank=True, 
        verbose_name='Единица измерения',
        help_text='Например: мм, кг, МГц'
    )
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок отображения')
    is_higher_better = models.BooleanField(
        default=False,
        verbose_name="Чем выше тем лучше",
        help_text="Определяет выделение лучшего значения в сравнениях"
    )

    class Meta:
        verbose_name = 'Поле характеристики'
        verbose_name_plural = 'Поля характеристик'
        ordering = ['category', 'order']

    def __str__(self):
        return f"{self.category.name} - {self.name}"

class DeviceImage(models.Model):
    device = models.ForeignKey('Device', related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='devices/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']


class Device(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(verbose_name='Описание', blank=True)
    main_image = models.ImageField(
        upload_to='devices/',
        verbose_name='Главное изображение',
        null=True,
        blank=True
    )
    category = models.ForeignKey(
        DeviceCategory, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Категория'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Устройство'
        verbose_name_plural = 'Устройства'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.name))
            original_slug = self.slug
            counter = 1
            while Device.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('comparisons:device_detail', kwargs={'slug': self.slug})
    
    def get_first_image(self):
        if self.main_image:
            return self.main_image
        first_image = self.images.first()
        return first_image.image if first_image else None

    def __str__(self):
        return self.name

class DeviceSpecification(models.Model):
    """Значение характеристики для конкретного устройства"""
    device = models.ForeignKey(
        'Device', 
        on_delete=models.CASCADE,
        related_name='specifications',
        verbose_name='Устройство'
    )
    field = models.ForeignKey(
        SpecificationField,
        on_delete=models.CASCADE,
        verbose_name='Характеристика',
        null=True,
        blank=True
    )
    value = models.CharField(
        max_length=255, 
        blank=True,
        verbose_name='Значение'
    )

    class Meta:
        verbose_name = 'Характеристика устройства'
        verbose_name_plural = 'Характеристики устройства'
        unique_together = ['device', 'field']

    def __str__(self):
        return f"{self.device.name} - {self.field.name if self.field else 'Без характеристики'}: {self.value}"

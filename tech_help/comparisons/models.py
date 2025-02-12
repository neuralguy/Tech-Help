from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.conf import settings
from django.urls import reverse
from unidecode import unidecode  # добавим для корректной транслитерации

class DeviceCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    slug = models.SlugField(unique=True, blank=True)
    
    class Meta:
        verbose_name = 'Категория устройств'
        verbose_name_plural = 'Категории устройств'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Specification(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    unit = models.CharField(max_length=50, verbose_name='Единица измерения', blank=True)
    is_higher_better = models.BooleanField(default=True, verbose_name='Чем больше, тем лучше')
    
    class Meta:
        verbose_name = 'Характеристика'
        verbose_name_plural = 'Характеристики'
    
    def __str__(self):
        return f"{self.name} ({self.unit})" if self.unit else self.name

class DeviceImage(models.Model):
    device = models.ForeignKey('Device', related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='devices/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Device(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(verbose_name='Описание')
    main_image = models.ImageField(
        upload_to='devices/', 
        verbose_name='Главное изображение',
        null=True,
        blank=True
    )
    category = models.ForeignKey(
        Category, 
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
            # Генерируем slug из названия, транслитерируя русские буквы
            self.slug = slugify(unidecode(self.name))
            
            # Если такой slug уже существует, добавляем число в конец
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
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='specifications', verbose_name='Устройство')
    specification = models.ForeignKey(Specification, on_delete=models.CASCADE, verbose_name='Характеристика')
    value = models.CharField(max_length=100, verbose_name='Значение')
    
    class Meta:
        verbose_name = 'Характеристика устройства'
        verbose_name_plural = 'Характеристики устройства'
        unique_together = ['device', 'specification']
    
    def __str__(self):
        return f"{self.device.name} - {self.specification.name}: {self.value}"

class Comparison(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название', blank=True)
    slug = models.SlugField(unique=True, blank=True)
    devices = models.ManyToManyField(Device, verbose_name='Устройства')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Создатель')
    created_date = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=True, verbose_name='Публичное сравнение')
    
    class Meta:
        verbose_name = 'Сравнение'
        verbose_name_plural = 'Сравнения'
        ordering = ['-created_date']
    
    def save(self, *args, **kwargs):
        if not self.title:
            devices_list = list(self.devices.all())
            if devices_list:
                self.title = f"Сравнение: {' vs '.join([device.name for device in devices_list[:3]])}"
                if len(devices_list) > 3:
                    self.title += " и другие"
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title

class ComparisonVote(models.Model):
    comparison = models.ForeignKey(Comparison, on_delete=models.CASCADE, related_name='votes', verbose_name='Сравнение')
    device = models.ForeignKey(Device, on_delete=models.CASCADE, verbose_name='Устройство')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Голос в сравнении'
        verbose_name_plural = 'Голоса в сравнении'
        unique_together = ['comparison', 'user']  # Один пользователь - один голос в сравнении
    
    def __str__(self):
        return f"Голос за {self.device.name} в {self.comparison.title}"

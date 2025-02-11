from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.conf import settings

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

class Device(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(DeviceCategory, on_delete=models.CASCADE, verbose_name='Категория')
    description = models.TextField(verbose_name='Описание')
    image = models.ImageField(upload_to='devices/', verbose_name='Изображение')
    release_date = models.DateField(verbose_name='Дата выпуска')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    manufacturer = models.CharField(max_length=100, verbose_name='Производитель')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Устройство'
        verbose_name_plural = 'Устройства'
        ordering = ['-created_date']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({self.manufacturer})"

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

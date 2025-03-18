from django.db import models
from django.utils.text import slugify
from django.conf import settings
from devices.models import Device

class Comparison(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название', blank=True)
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
        # Генерация заголовка, если он не задан
        if not self.title:
            devices_list = list(self.devices.all())
            if devices_list:
                self.title = f"Сравнение: {' vs '.join([device.name for device in devices_list[:3]])}"
                if len(devices_list) > 3:
                    self.title += " и другие"
        
        # Генерация slug, если он не задан
        if not self.slug:
            base_slug = slugify(self.title)
            unique_slug = base_slug
            num = 1
            while Comparison.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{num}"
                num += 1
            self.slug = unique_slug
        
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

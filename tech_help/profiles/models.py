from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from articles.models import Article
from comparisons.models import Comparison, Device

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png', verbose_name='Аватар')
    favorite_articles = models.ManyToManyField(Article, blank=True, related_name='favorited_by', verbose_name='Избранные статьи')
    favorite_devices = models.ManyToManyField(Device, blank=True, related_name='favorited_by', verbose_name='Избранные устройства')
    
    # Статистика
    articles_read = models.PositiveIntegerField(default=0, verbose_name='Прочитано статей')
    comments_count = models.PositiveIntegerField(default=0, verbose_name='Количество комментариев')
    comparisons_created = models.PositiveIntegerField(default=0, verbose_name='Создано сравнений')
    votes_count = models.PositiveIntegerField(default=0, verbose_name='Количество голосов')
    
    # Настройки уведомлений
    notify_on_comment_reply = models.BooleanField(default=True, verbose_name='Уведомлять об ответах на комментарии')
    notify_on_article_update = models.BooleanField(default=True, verbose_name='Уведомлять об обновлениях избранных статей')
    notify_on_device_update = models.BooleanField(default=True, verbose_name='Уведомлять об обновлениях избранных устройств')

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return f'Профиль пользователя {self.user.username}'

class Achievement(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    icon = models.ImageField(upload_to='achievements/', verbose_name='Иконка')
    condition_value = models.PositiveIntegerField(verbose_name='Значение для получения')
    condition_type = models.CharField(
        max_length=50,
        choices=[
            ('articles_read', 'Прочитано статей'),
            ('comments_count', 'Написано комментариев'),
            ('comparisons_created', 'Создано сравнений'),
            ('votes_count', 'Сделано голосов'),
        ],
        verbose_name='Тип достижения'
    )

    class Meta:
        verbose_name = 'Достижение'
        verbose_name_plural = 'Достижения'

    def __str__(self):
        return self.name

class UserAchievement(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    date_earned = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Достижение пользователя'
        verbose_name_plural = 'Достижения пользователей'
        unique_together = ['user', 'achievement']

    def __str__(self):
        return f'{self.user.username} - {self.achievement.name}'

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

from django.contrib import admin
from .models import Profile, Achievement, UserAchievement

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'articles_read', 'comments_count', 'comparisons_created', 'votes_count')
    list_filter = ('notify_on_comment_reply', 'notify_on_article_update', 'notify_on_device_update')
    search_fields = ('user__username', 'user__email')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'avatar')
        }),
        ('Избранное', {
            'fields': ('favorite_articles', 'favorite_devices')
        }),
        ('Статистика', {
            'fields': ('articles_read', 'comments_count', 'comparisons_created', 'votes_count')
        }),
        ('Настройки уведомлений', {
            'fields': ('notify_on_comment_reply', 'notify_on_article_update', 'notify_on_device_update')
        }),
    )
    
    readonly_fields = ('articles_read', 'comments_count', 'comparisons_created', 'votes_count')

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('name', 'condition_type', 'condition_value')
    list_filter = ('condition_type',)
    search_fields = ('name', 'description')

class UserAchievementInline(admin.TabularInline):
    model = UserAchievement
    extra = 0
    readonly_fields = ('date_earned',)
    can_delete = False

@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievement', 'date_earned')
    list_filter = ('achievement', 'date_earned')
    search_fields = ('user__username', 'achievement__name')
    readonly_fields = ('date_earned',)

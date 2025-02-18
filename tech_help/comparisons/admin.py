from django.contrib import admin
from .models import (
    Comparison,
    ComparisonVote
)

@admin.register(Comparison)
class ComparisonAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'created_date', 'is_public']
    list_filter = ['is_public', 'created_date']
    search_fields = ['title']
    filter_horizontal = ['devices']

@admin.register(ComparisonVote)
class ComparisonVoteAdmin(admin.ModelAdmin):
    list_display = ['comparison', 'device', 'user', 'created_date']
    list_filter = ['created_date']
    search_fields = ['comparison__title', 'device__name', 'user__username']

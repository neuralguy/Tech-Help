from django.contrib import admin
from .models import (
    Device, 
    DeviceCategory, 
    DeviceImage, 
    SpecificationCategory, 
    SpecificationField, 
    DeviceSpecification,
    Comparison,
    ComparisonVote
)

class SpecificationFieldInline(admin.TabularInline):
    model = SpecificationField
    extra = 1

@admin.register(SpecificationCategory)
class SpecificationCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order']
    search_fields = ['name']
    ordering = ['order']
    inlines = [SpecificationFieldInline]

class DeviceSpecificationInline(admin.TabularInline):
    model = DeviceSpecification
    extra = 1
    autocomplete_fields = ['field']

class DeviceImageInline(admin.TabularInline):
    model = DeviceImage
    extra = 1

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'created_at']
    list_filter = ['category']
    search_fields = ['name', 'description']
    inlines = [DeviceImageInline, DeviceSpecificationInline]
    prepopulated_fields = {'slug': ('name',)}

@admin.register(DeviceCategory)
class DeviceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(SpecificationField)
class SpecificationFieldAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'unit', 'order']
    list_filter = ['category']
    search_fields = ['name', 'description']
    ordering = ['category', 'order']

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

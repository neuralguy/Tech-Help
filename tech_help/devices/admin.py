from django.contrib import admin
from .models import (
    Device, 
    DeviceCategory, 
    DeviceImage, 
    SpecificationCategory, 
    SpecificationField, 
    DeviceSpecification,
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


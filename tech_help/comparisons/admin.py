from django.contrib import admin
from .models import DeviceCategory, Specification, Device, DeviceSpecification, Comparison, ComparisonVote

@admin.register(DeviceCategory)
class DeviceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Specification)
class SpecificationAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit', 'is_higher_better')
    list_filter = ('is_higher_better',)
    search_fields = ('name', 'unit')

class DeviceSpecificationInline(admin.TabularInline):
    model = DeviceSpecification
    extra = 1
    autocomplete_fields = ['specification']

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'manufacturer', 'category', 'price', 'release_date')
    list_filter = ('category', 'manufacturer', 'release_date')
    search_fields = ('name', 'manufacturer', 'description')
    prepopulated_fields = {'slug': ('name',)}
    date_hierarchy = 'release_date'
    inlines = [DeviceSpecificationInline]
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'category', 'manufacturer', 'description')
        }),
        ('Медиа', {
            'fields': ('image',)
        }),
        ('Дополнительная информация', {
            'fields': ('price', 'release_date')
        }),
    )

@admin.register(DeviceSpecification)
class DeviceSpecificationAdmin(admin.ModelAdmin):
    list_display = ('device', 'specification', 'value')
    list_filter = ('specification', 'device')
    search_fields = ('device__name', 'specification__name', 'value')
    autocomplete_fields = ['device', 'specification']

class ComparisonVoteInline(admin.TabularInline):
    model = ComparisonVote
    extra = 0
    readonly_fields = ('user', 'device', 'created_date')
    can_delete = False

@admin.register(Comparison)
class ComparisonAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'created_date', 'is_public', 'device_count')
    list_filter = ('is_public', 'created_date')
    search_fields = ('title', 'created_by__username')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('devices',)
    inlines = [ComparisonVoteInline]
    readonly_fields = ('created_by', 'created_date')

    def device_count(self, obj):
        return obj.devices.count()
    device_count.short_description = 'Количество устройств'

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(ComparisonVote)
class ComparisonVoteAdmin(admin.ModelAdmin):
    list_display = ('comparison', 'device', 'user', 'created_date')
    list_filter = ('created_date', 'device')
    search_fields = ('comparison__title', 'device__name', 'user__username')
    readonly_fields = ('created_date',)

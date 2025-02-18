from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Comparison, ComparisonVote
from devices.models import Device
from collections import defaultdict
from django.views.decorators.cache import never_cache

@login_required
def comparison_create(request):
    if request.method == 'POST':
        device_ids = request.POST.getlist('devices')
        if len(device_ids) >= 2:
            comparison = Comparison.objects.create(
                created_by=request.user,
                title="Сравнение устройств"
            )
            comparison.devices.set(device_ids)
            if not comparison.slug:
                comparison.save()
            return redirect('comparisons:comparison_detail', slug=comparison.slug)
    
    devices = Device.objects.all().order_by('-created_at')
    context = {
        'devices': devices,
    }
    return render(request, 'comparisons/comparison_create.html', context)

@never_cache
def comparison_detail(request, slug):
    comparison = get_object_or_404(Comparison, slug=slug)
    devices = comparison.devices.all()
    
    # Инициализируем структуру данных
    specifications = {}
    
    for device in devices:
        for spec in device.specifications.all().select_related('field__category'):
            category = spec.field.category.name if spec.field.category else "Общие"
            field_name = spec.field.name
            field_unit = spec.field.unit
            
            if category not in specifications:
                specifications[category] = {}
            
            if field_name not in specifications[category]:
                specifications[category][field_name] = {
                    'unit': field_unit,
                    'values': {},
                    'is_higher_better': spec.field.is_higher_better
                }
            
            specifications[category][field_name]['values'][device.id] = spec.value

    context = {
        'comparison': comparison,
        'devices': devices,
        'specifications': specifications.items(),  # Преобразуем в список пар
        'user_vote': None
    }
    
    if request.user.is_authenticated:
        context['user_vote'] = ComparisonVote.objects.filter(
            comparison=comparison,
            user=request.user
        ).first()
    
    return render(request, 'comparisons/comparison_detail.html', context)

@login_required
def vote_for_device(request, comparison_slug, device_slug):
    comparison = get_object_or_404(Comparison, slug=comparison_slug)
    device = get_object_or_404(Device, slug=device_slug)
    
    if device in comparison.devices.all():
        ComparisonVote.objects.update_or_create(
            comparison=comparison,
            user=request.user,
            defaults={'device': device}
        )
    
    return redirect('comparisons:comparison_detail', slug=comparison_slug)

def comparison_list(request):
    comparisons = Comparison.objects.all().order_by('-created_date')
    return render(request, 'comparisons/comparison_list.html', {
        'comparisons': comparisons
    })


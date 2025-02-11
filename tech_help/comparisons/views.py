from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from .models import Device, DeviceCategory, Comparison, ComparisonVote, Specification
from django.contrib import messages
from .forms import DeviceForm, SpecificationForm

def device_list(request):
    devices = Device.objects.all().order_by('-created_date')
    categories = DeviceCategory.objects.all()
    
    # Фильтрация по категории
    category_slug = request.GET.get('category')
    if category_slug:
        devices = devices.filter(category__slug=category_slug)
    
    # Поиск по названию
    search_query = request.GET.get('search')
    if search_query:
        devices = devices.filter(
            Q(name__icontains=search_query) | 
            Q(manufacturer__icontains=search_query)
        )
    
    context = {
        'devices': devices,
        'categories': categories,
        'current_category': category_slug,
        'search_query': search_query,
    }
    return render(request, 'comparisons/device_list.html', context)

def device_detail(request, slug):
    device = get_object_or_404(Device, slug=slug)
    similar_devices = Device.objects.filter(
        category=device.category
    ).exclude(id=device.id)[:3]
    
    context = {
        'device': device,
        'similar_devices': similar_devices,
    }
    return render(request, 'comparisons/device_detail.html', context)

@login_required
def comparison_create(request):
    if request.method == 'POST':
        device_ids = request.POST.getlist('devices')
        if len(device_ids) >= 2:
            comparison = Comparison.objects.create(
                created_by=request.user,
                title=f"Сравнение устройств"
            )
            comparison.devices.set(device_ids)
            return redirect('comparisons:comparison_detail', slug=comparison.slug)
    
    devices = Device.objects.all().order_by('-created_date')
    context = {
        'devices': devices,
    }
    return render(request, 'comparisons/comparison_create.html', context)

def comparison_detail(request, slug):
    comparison = get_object_or_404(Comparison, slug=slug)
    devices = comparison.devices.all()
    
    # Получаем все уникальные характеристики для устройств
    specs = {}
    for device in devices:
        for spec in device.specifications.all():
            if spec.specification.name not in specs:
                specs[spec.specification.name] = {
                    'unit': spec.specification.unit,
                    'is_higher_better': spec.specification.is_higher_better,
                    'values': {}
                }
            specs[spec.specification.name]['values'][device.id] = spec.value
    
    # Получаем голос пользователя
    user_vote = None
    if request.user.is_authenticated:
        user_vote = ComparisonVote.objects.filter(
            comparison=comparison,
            user=request.user
        ).first()
    
    context = {
        'comparison': comparison,
        'devices': devices,
        'specifications': specs,
        'user_vote': user_vote,
    }
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

def get_device_specs(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        device_id = request.GET.get('device_id')
        if device_id:
            device = get_object_or_404(Device, id=device_id)
            specs = [{
                'name': spec.specification.name,
                'value': spec.value,
                'unit': spec.specification.unit
            } for spec in device.specifications.all()]
            return JsonResponse({'specs': specs})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def device_create(request):
    if request.method == 'POST':
        form = DeviceForm(request.POST, request.FILES)
        if form.is_valid():
            device = form.save()
            messages.success(request, 'Устройство успешно добавлено!')
            return redirect('comparisons:device_detail', slug=device.slug)
    else:
        form = DeviceForm()
    
    # Получаем все существующие спецификации для автозаполнения
    specs = Specification.objects.all().values('name', 'unit', 'is_higher_better')
    
    return render(request, 'comparisons/device_form.html', {
        'form': form,
        'specifications': list(specs),
        'title': 'Добавить устройство'
    })

@login_required
def device_edit(request, slug):
    device = get_object_or_404(Device, slug=slug)
    
    if not request.user.is_staff:
        messages.error(request, 'У вас нет прав на редактирование устройств.')
        return redirect('comparisons:device_detail', slug=slug)
    
    if request.method == 'POST':
        form = DeviceForm(request.POST, request.FILES, instance=device)
        if form.is_valid():
            device = form.save()
            messages.success(request, 'Устройство успешно обновлено!')
            return redirect('comparisons:device_detail', slug=device.slug)
    else:
        # Подготавливаем текущие спецификации для формы
        current_specs = [
            {
                'name': spec.specification.name,
                'unit': spec.specification.unit,
                'value': spec.value,
                'is_higher_better': spec.specification.is_higher_better
            }
            for spec in device.specifications.all()
        ]
        initial = {'specifications': current_specs}
        form = DeviceForm(instance=device, initial=initial)
    
    specs = Specification.objects.all().values('name', 'unit', 'is_higher_better')
    
    return render(request, 'comparisons/device_form.html', {
        'form': form,
        'device': device,
        'specifications': list(specs),
        'title': 'Редактировать устройство'
    })

@login_required
def specification_create(request):
    if not request.user.is_staff:
        messages.error(request, 'У вас нет прав на создание спецификаций.')
        return redirect('comparisons:device_list')
    
    if request.method == 'POST':
        form = SpecificationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Спецификация успешно создана!')
            return redirect('comparisons:specification_list')
    else:
        form = SpecificationForm()
    
    return render(request, 'comparisons/specification_form.html', {
        'form': form,
        'title': 'Создать спецификацию'
    })

def comparison_list(request):
    comparisons = Comparison.objects.all().order_by('-created_date')
    return render(request, 'comparisons/comparison_list.html', {
        'comparisons': comparisons
    })

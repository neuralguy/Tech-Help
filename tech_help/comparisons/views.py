from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from .models import Device, DeviceCategory, Comparison, ComparisonVote, DeviceImage, DeviceSpecification, SpecificationCategory, SpecificationField
from django.contrib import messages
from .forms import DeviceForm, DeviceSpecificationFormSet, DeviceSpecificationForm, SpecificationFieldForm

def device_list(request):
    devices = Device.objects.all().order_by('-created_at')
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
    # Группируем характеристики по категориям
    specifications = {}
    for category in SpecificationCategory.objects.all():
        specs = device.specifications.filter(field__category=category).select_related('field')
        if specs.exists():
            specifications[category] = specs
    
    return render(request, 'comparisons/device_detail.html', {
        'device': device,
        'specifications': specifications,
    })

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
    
    devices = Device.objects.all().order_by('-created_at')
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
            if spec.field.name not in specs:
                specs[spec.field.name] = {
                    'unit': spec.field.unit,
                    'values': {}
                }
            specs[spec.field.name]['values'][device.id] = spec.value
    
    context = {
        'comparison': comparison,
        'devices': devices,
        'specifications': specs,
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
            
            # Обработка изображений
            for image in request.FILES.getlist('images'):
                DeviceImage.objects.create(device=device, image=image)
            
            # Обработка спецификаций
            formset = DeviceSpecificationFormSet(request.POST, instance=device)
            if formset.is_valid():
                formset.save()
                messages.success(request, 'Устройство успешно создано.')
                return redirect('comparisons:device_detail', slug=device.slug)
    else:
        form = DeviceForm()
        formset = DeviceSpecificationFormSet()
    
    categories = SpecificationCategory.objects.prefetch_related('fields').all()
    
    return render(request, 'comparisons/device_form.html', {
        'form': form,
        'formset': formset,
        'categories': categories,
        'title': 'Создание устройства'
    })

@login_required
def device_edit(request, slug):
    device = get_object_or_404(Device, slug=slug)
    
    if request.method == 'POST':
        form = DeviceForm(request.POST, request.FILES, instance=device)
        formset = DeviceSpecificationFormSet(request.POST, instance=device)
        
        if form.is_valid():
            device = form.save()
            
            # Обработка изображений
            for image in request.FILES.getlist('images'):
                DeviceImage.objects.create(device=device, image=image)
            
            # Обработка спецификаций
            if formset.is_valid():
                formset.save()
                messages.success(request, 'Устройство успешно обновлено.')
                return redirect('comparisons:device_detail', slug=device.slug)
    else:
        form = DeviceForm(instance=device)
        formset = DeviceSpecificationFormSet(instance=device)
    
    return render(request, 'comparisons/device_form.html', {
        'form': form,
        'formset': formset,
        'device': device,
        'title': 'Редактирование устройства',
        'categories': SpecificationCategory.objects.prefetch_related('fields').all()
    })

@login_required
def specification_create(request):
    if not request.user.is_staff:
        messages.error(request, 'У вас нет прав на создание спецификаций.')
        return redirect('comparisons:device_list')
    
    if request.method == 'POST':
        form = SpecificationFieldForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Характеристика успешно создана!')
            return redirect('comparisons:device_list')
    else:
        form = SpecificationFieldForm()
    
    return render(request, 'comparisons/specification_form.html', {
        'form': form,
        'title': 'Создать характеристику'
    })

def comparison_list(request):
    comparisons = Comparison.objects.all().order_by('-created_date')
    return render(request, 'comparisons/comparison_list.html', {
        'comparisons': comparisons
    })

@login_required
def device_delete(request, slug):
    device = get_object_or_404(Device, slug=slug)
    
    if request.method == 'POST':
        device.delete()
        messages.success(request, 'Устройство успешно удалено.')
        return redirect('comparisons:device_list')
        
    return render(request, 'comparisons/device_confirm_delete.html', {
        'device': device
    })

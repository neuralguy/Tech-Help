from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from .models import Device, DeviceCategory, DeviceImage, SpecificationCategory
from django.contrib import messages
from .forms import DeviceForm, DeviceSpecificationFormSet, SpecificationFieldForm


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
    return render(request, 'devices/device_list.html', context)

def device_detail(request, slug):
    device = get_object_or_404(Device, slug=slug)
    # Группируем характеристики по категориям
    specifications = {}
    for category in SpecificationCategory.objects.all():
        specs = device.specifications.filter(field__category=category).select_related('field')
        if specs.exists():
            specifications[category] = specs
    
    return render(request, 'devices/device_detail.html', {
        'device': device,
        'specifications': specifications,
    })


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
        form = DeviceForm(request.POST)
        if form.is_valid():
            device = form.save(commit=False)
            
            # Обработка главного изображения
            if 'main_image' in request.FILES:
                device.main_image = request.FILES['main_image']
            
            device.save()
            
            # Обработка дополнительных изображений
            for image in request.FILES.getlist('images'):
                DeviceImage.objects.create(device=device, image=image)
            
            # Обработка спецификаций
            formset = DeviceSpecificationFormSet(request.POST, instance=device)
            if formset.is_valid():
                formset.save()
                messages.success(request, 'Устройство успешно создано.')
                return redirect('devices:device_detail', slug=device.slug)
    else:
        form = DeviceForm()
        formset = DeviceSpecificationFormSet()
    
    categories = SpecificationCategory.objects.prefetch_related('fields').all()
    
    return render(request, 'devices/device_form.html', {
        'form': form,
        'formset': formset,
        'categories': categories,
        'title': 'Создание устройства'
    })


@login_required
def device_edit(request, slug):
    device = get_object_or_404(Device, slug=slug)
    
    if request.method == 'POST':
        form = DeviceForm(request.POST, instance=device)
        formset = DeviceSpecificationFormSet(request.POST, instance=device)
        
        if form.is_valid():
            device = form.save(commit=False)
            
            # Обработка главного изображения
            if 'main_image' in request.FILES:
                device.main_image = request.FILES['main_image']
            
            device.save()
            
            # Обработка дополнительных изображений
            for image in request.FILES.getlist('images'):
                DeviceImage.objects.create(device=device, image=image)
            
            # Обработка спецификаций
            if formset.is_valid():
                formset.save()
                messages.success(request, 'Устройство успешно обновлено.')
                return redirect('devices:device_detail', slug=device.slug)
    else:
        form = DeviceForm(instance=device)
        formset = DeviceSpecificationFormSet(instance=device)
    
    return render(request, 'devices/device_form.html', {
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
        return redirect('devices:device_list')
    
    if request.method == 'POST':
        form = SpecificationFieldForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Характеристика успешно создана!')
            return redirect('devices:device_list')
    else:
        form = SpecificationFieldForm()
    
    return render(request, 'devices/specification_form.html', {
        'form': form,
        'title': 'Создать характеристику'
    })


@login_required
def device_delete(request, slug):
    device = get_object_or_404(Device, slug=slug)
    
    if request.method == 'POST':
        device.delete()
        messages.success(request, 'Устройство успешно удалено.')
        return redirect('devices:device_list')
        
    return render(request, 'devices/device_confirm_delete.html', {
        'device': device
    })
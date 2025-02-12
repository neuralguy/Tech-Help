from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from .models import Device, DeviceCategory, Comparison, ComparisonVote, Specification, DeviceImage, Category
from django.contrib import messages
from .forms import DeviceForm, SpecificationForm

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
    return render(request, 'comparisons/device_detail.html', {
        'device': device,
        'images': device.images.all()
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
        print("FILES:", request.FILES)  # Отладка
        print("POST:", request.POST)    # Отладка
        
        if form.is_valid():
            device = form.save()
            
            # Обработка дополнительных изображений
            images = request.FILES.getlist('images')
            print("Additional images:", images)  # Отладка
            
            if images:
                for order, image in enumerate(images):
                    DeviceImage.objects.create(
                        device=device,
                        image=image,
                        order=order
                    )
                messages.success(request, 'Устройство и изображения успешно созданы!')
            else:
                messages.success(request, 'Устройство успешно создано!')
            
            return redirect('comparisons:device_detail', slug=device.slug)
        else:
            print("Form errors:", form.errors)  # Отладка
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = DeviceForm()
    
    return render(request, 'comparisons/device_form.html', {'form': form})

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
            
            # Вот тут была ошибка - нужно брать файлы напрямую из request.FILES.getlist
            for image in request.FILES.getlist('images'):
                DeviceImage.objects.create(
                    device=device,
                    image=image,
                    order=device.images.count()
                )
            
            return redirect('comparisons:device_detail', slug=device.slug)
        else:
            print("Form errors:", form.errors)  # Отладка
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = DeviceForm(instance=device)
    
    specs = Specification.objects.all().values('name', 'unit', 'is_higher_better')
    
    return render(request, 'comparisons/device_form.html', {
        'form': form,
        'device': device,
        'specifications': list(specs),
        'title': 'Редактировать устройство',
        'existing_images': device.images.all()
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

@login_required
def device_delete(request, slug):
    device = get_object_or_404(Device, slug=slug)
    
    if request.method == 'POST':
        device.delete()
        messages.success(request, 'Устройство успешно удалено')
        return redirect('comparisons:device_list')
        
    return render(request, 'comparisons/device_confirm_delete.html', {
        'device': device
    })

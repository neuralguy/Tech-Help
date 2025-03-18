from django import forms
from .models import (
    Device, 
    DeviceSpecification, 
    SpecificationCategory, 
    SpecificationField
)


class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['name', 'category', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input w-full rounded-lg border-gray-700 bg-gray-800 text-white',
                'placeholder': 'Название устройства'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select w-full rounded-lg border-gray-700 bg-gray-800 text-white'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea w-full rounded-lg border-gray-700 bg-gray-800 text-white',
                'rows': 3,
                'placeholder': 'Описание устройства'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'specifications':
                self.fields[field].widget.attrs.update({'class': 'form-input'})

    def save(self, commit=True):
        device = super().save(commit=commit)
        if commit and self.cleaned_data.get('specifications'):
            # Удаляем старые спецификации
            device.specifications.all().delete()
            # Добавляем новые
            specs_data = self.cleaned_data['specifications']
            for spec_data in specs_data:
                spec, _ = SpecificationField.objects.get_or_create(
                    name=spec_data['name'],
                    defaults={'unit': spec_data.get('unit', '')}
                )
                DeviceSpecification.objects.create(
                    device=device,
                    specification=spec,
                    value=spec_data['value']
                )
        return device

    def clean_images(self):
        """Метод для обработки дополнительных изображений"""
        return self.files.getlist('images')

class DeviceSpecificationForm(forms.ModelForm):
    class Meta:
        model = DeviceSpecification
        fields = ['field', 'value']
        widgets = {
            'field': forms.HiddenInput(),
            'value': forms.TextInput(attrs={
                'class': 'form-input w-full rounded-lg border-gray-700 bg-gray-800 text-white'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.field:
            self.fields['field'].initial = self.instance.field
            if self.instance.field.unit:
                self.fields['value'].widget.attrs['placeholder'] = f'Введите значение в {self.instance.field.unit}'

class SpecificationFieldForm(forms.ModelForm):
    class Meta:
        model = SpecificationField
        fields = ['name', 'category', 'description', 'unit', 'order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
            'unit': forms.TextInput(attrs={'class': 'form-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-input'})
        }

class BaseDeviceSpecificationFormSet(forms.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.categories = {}
        
        categories = SpecificationCategory.objects.prefetch_related('fields').all()
        
        for category in categories:
            self.categories[category] = []
            for field in category.fields.all():
                existing_spec = None
                if self.instance.pk:
                    existing_spec = self.instance.specifications.filter(field=field).first()
                
                form = DeviceSpecificationForm(
                    data=self.data if self.data else None,
                    prefix=f'spec_{field.id}',
                    instance=existing_spec or DeviceSpecification(device=self.instance, field=field),
                    initial={'field': field.id}
                )
                self.categories[category].append(form)

    def is_valid(self):
        valid = True
        for category_forms in self.categories.values():
            for form in category_forms:
                if form.is_valid():
                    continue
                valid = False
        return valid

    def save(self, commit=True):
        specs = []
        if commit:
            # Сохраняем только заполненные спецификации
            for category_forms in self.categories.values():
                for form in category_forms:
                    if form.is_valid() and form.cleaned_data.get('value'):
                        spec = form.save(commit=False)
                        spec.device = self.instance
                        spec.save()
                        specs.append(spec)
            
            # Удаляем старые спецификации, которые не были обновлены
            self.instance.specifications.exclude(
                id__in=[spec.id for spec in specs]
            ).delete()
        
        return specs

# Создаем FormSet для спецификаций устройства
DeviceSpecificationFormSet = forms.inlineformset_factory(
    Device,
    DeviceSpecification,
    form=DeviceSpecificationForm,
    formset=BaseDeviceSpecificationFormSet,
    extra=0,
    can_delete=False
) 
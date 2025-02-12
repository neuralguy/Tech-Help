from django import forms
from .models import (
    Device, 
    DeviceCategory, 
    DeviceSpecification, 
    SpecificationCategory, 
    SpecificationField
)

class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['name', 'category', 'description', 'slug']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
            'slug': forms.TextInput(attrs={'class': 'form-input'}),
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
            'value': forms.TextInput(attrs={'class': 'form-input'})
        }

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

# Создаем FormSet для спецификаций устройства
DeviceSpecificationFormSet = forms.inlineformset_factory(
    Device,
    DeviceSpecification,
    form=DeviceSpecificationForm,
    extra=0,
    can_delete=True
) 
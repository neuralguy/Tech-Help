from django import forms
from .models import Device, DeviceCategory, Specification, DeviceSpecification

class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['name', 'description', 'main_image', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full rounded-lg border-gray-300 bg-white text-gray-900'}),
            'description': forms.Textarea(attrs={'class': 'w-full rounded-lg border-gray-300 bg-white text-gray-900', 'rows': 4}),
            'main_image': forms.FileInput(attrs={'class': 'w-full rounded-lg border-gray-300 bg-white text-gray-900'}),
            'category': forms.Select(attrs={'class': 'w-full rounded-lg border-gray-300 bg-white text-gray-900'}),
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
                spec, _ = Specification.objects.get_or_create(
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

class SpecificationForm(forms.ModelForm):
    class Meta:
        model = Specification
        fields = ['name', 'unit', 'is_higher_better']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Например: Процессор'}),
            'unit': forms.TextInput(attrs={'placeholder': 'Например: ГГц'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-input'}) 
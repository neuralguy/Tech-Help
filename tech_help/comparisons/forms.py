from django import forms
from .models import Device, DeviceCategory, Specification, DeviceSpecification

class DeviceForm(forms.ModelForm):
    specifications = forms.JSONField(required=False, widget=forms.HiddenInput())
    
    class Meta:
        model = Device
        fields = ['name', 'manufacturer', 'category', 'price', 'release_date', 
                 'image', 'description', 'specifications']
        widgets = {
            'release_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
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
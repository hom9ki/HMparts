from django import forms
from .models import Garage, Model, UserCar, Brand


class GarageForm(forms.Form):
    model = forms.ModelChoiceField(queryset=Model.objects.all(), empty_label='Выберите модель',
                                   label='Модель', required=True)

    class Meta:
        model = Garage


class AddCarForm(forms.ModelForm):
    brand = forms.ModelChoiceField(
        queryset=Brand.objects.all(),
        widget=forms.Select(
            attrs={'class': 'form-select'}
        ),
        label='Марка авто'
    )

    class Meta:
        model = UserCar
        fields = ['car_model', 'is_main']
        widgets = {
            'car_model': forms.Select(attrs={'class': 'form-select'}),
            'is_main': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['car_model'].queryset = Model.objects.select_related('brand').order_by('brand__name', 'name')


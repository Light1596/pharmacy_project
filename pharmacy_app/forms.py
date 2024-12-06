from django import forms
from pharmacy_app.models import Medicine

class MedicineForm(forms.ModelForm):
    CATEGORY_CHOICES = [
        ('Painkillers', 'Painkillers'),
        ('Antibiotics', 'Antibiotics'),
        ('Vitamins', 'Vitamins'),
        ('Cold and Flu', 'Cold and Flu'),
        ('Skin Care', 'Skin Care'),
        ('Digestive Health', 'Digestive Health'),
    ]

    category = forms.ChoiceField(choices=CATEGORY_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Medicine
        fields = '__all__'
from django import forms
from pharmacy_app.models import Medicine

class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = '__all__'
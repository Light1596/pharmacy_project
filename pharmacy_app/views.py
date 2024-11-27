from django.contrib.auth import login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from pharmacy_app.models import Medicine
from pharmacy_app.forms import MedicineForm

# Create your views here.
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been created successfully. You can now log in')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form':form})


def home(request):
    return render(request, 'home.html')

# List all medicines
def medicine_list(request):
    medicines = Medicine.objects.all()
    return render(request, 'medicine_list.html', {'medicines': medicines})

# create a new medicine
@login_required
def medicine_create(request):
    if request.method == 'POST':
        form = MedicineForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('medicine_list')
    else:
        form = MedicineForm()
    return render(request, 'medicine_form.html',{'form': form})

# Update an existing medicine
@login_required
def medicine_update(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        form =MedicineForm(request.POST, instance=medicine)
        if form.is_valid():
            form.save()
            return redirect('medicine_list')
    else:
        form = MedicineForm(instance=medicine)
    return render(request, 'medicine_form.html',{'form': form})

# Delete a medicine
@login_required
def medicine_delete(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        medicine.delete()
        return redirect('medicine_list')
    return render(request, 'medicine_confirm_delete.html', {'medicine':medicine})
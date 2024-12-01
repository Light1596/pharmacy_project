from django.contrib.auth import login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from pharmacy_app.models import Medicine, CartItem
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
    query = request.GET.get('query')
    category = request.GET.get('category')

    if query:
        medicines = medicines.filter(name__icontains=query)
    if category:
        medicines = medicines.filter(category__iexact=category)
    return render(request, 'medicine_list.html', {'medicines': medicines})

# create a new medicine
@login_required
def medicine_create(request):
    if request.method == 'POST':
        form = MedicineForm(request.POST, request.FILES)
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

@login_required
def cart_view(request):
    cart_items = []
    total_price = 0

    for item in request.session.get('cart', []):
        medicine = Medicine.objects.get(id=item['medicine_id'])
        quantity = item['quantity']
        item_total = medicine.price * quantity
        total_price += item_total
        cart_items.append({
            'medicine': medicine,
            'quantity': quantity,
            'item_total': item_total,
        })

    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})

# Add an item to the cart
@login_required
def add_to_cart(request,pk):

    medicine = get_object_or_404(Medicine, pk=pk)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, medicine=medicine)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart')

# Remove an item from the cart
@login_required
def remove_from_cart(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk, user=request.user)
    cart_item.delete()
    return redirect('cart')

# Checkout
@login_required
def checkout_view(request):
    if request.method == 'POST':
        CartItem.objects.filter(user=request.user).delete() # Clear the cart after checkout
        return render(request, 'checkout_complete.html')
    return render(request, 'checkout.html')
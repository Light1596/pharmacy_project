from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserChangeForm
from django.db.models.signals import post_save
from django.dispatch import receiver

from pharmacy_app.models import Medicine, CartItem, UserProfile
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
    # Query medicines by category (example categories: 'Painkillers', 'Antibiotics', etc.)
    medicines_by_category = {
        'Painkillers': Medicine.objects.filter(category='Painkillers')[:4],
        'Antibiotics': Medicine.objects.filter(category='Antibiotics')[:4],
        'Vitamins': Medicine.objects.filter(category='Vitamins')[:4],
    }

    # Carousel images (replace with actual file paths or image URLs from your static folder)
    carousel_images = [
        'images/medicine2.jpg',
        'images/capsules.jpg',
        'images/tablets.jpg',
    ]

    # Context to pass to the template
    context = {
        'medicines_by_category': medicines_by_category,
        'carousel_images': carousel_images,
    }

    return render(request, 'base.html', context)


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

@login_required
def view_profile(request):
    user = request.user
    profile = user.profile if hasattr(user, 'profile') else None
    context = {
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'date_joined': user.date_joined,
        'last_login': user.last_login,
        'is_staff': user.is_staff,
        'profile': profile,
    }
    return render(request, 'profile.html', context)

@login_required
def edit_profile(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)

        if 'image' in request.FILES:
            profile.image = request.FILES['image']

        user.save()
        profile.save()

        return redirect('view_profile')

    return render(request, 'edit_profile.html', {'user': user, 'profile': profile})


@receiver(post_save, sender=User)
def create_r_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.profile.save()

def about_us(request):
    return render(request, 'about_us.html')

def services(request):
    return render(request, 'services.html')
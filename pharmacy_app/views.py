from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserChangeForm
from django.db.models.signals import post_save
from django.dispatch import receiver
from unicodedata import category

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
    medicines = Medicine.objects.all()
    # Query medicines by category (example categories: 'Painkillers', 'Antibiotics', etc.)
    medicines_by_category = {
        'Painkillers': Medicine.objects.filter(category='Painkillers')[:4],
        'Antibiotics': Medicine.objects.filter(category='Antibiotics')[:4],
        'Vitamins': Medicine.objects.filter(category='Vitamins')[:4],
        'Cold and Flu' : Medicine.objects.filter(category='Cold and Flu')[:4],
        'Skin Care' : Medicine.objects.filter(category='Skin Care')[:4],
        'Digestive Health' : Medicine.objects.filter(category='Digestive Health')[:4]
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

    return render(request, 'home.html', context)


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
            print(form.errors)
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
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.medicine.price * item.quantity for item in cart_items)

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


@login_required
def remove_from_cart(request, pk):
    try:
        cart_item = CartItem.objects.get(pk=pk, user=request.user)
        cart_item.delete()
        return redirect('cart')
    except CartItem.DoesNotExist:
        raise Http404("Cart item does not exist.")

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

@login_required()
def upload_prescription(request):
    if request.method == 'POST':
        prescription_file = request.FILES['prescription']
        doctor_email = 'lightsimiyu@gmail.com'
        send_mail(
            'New Prescription Uploaded',
            f'A new prescription has been uploaded by {request.user.username}.',
            settings.EMAIL_HOST_USER,
            [doctor_email],
            fail_silently=False,
        )
        messages.success(request, "Prescription uploaded successfully and sent to the doctor.")
        return redirect('services')
    return render(request, 'services.html')

def book_consultation(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        message = request.POST['message']
        doctor_email = 'lightsimiyu@gmail.com'
        send_mail(
            'Consultation Request',
            f'Name: {name}\nEmail: {email}\nMessage: {message}',
            settings.EMAIL_HOST_USER,
            [doctor_email],
            fail_silently=False,
        )
        messages.success(request, "Consultation request sent successfully.")
        return redirect('services')
    return render(request, 'services.html')

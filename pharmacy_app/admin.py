from django.contrib import admin

from pharmacy_app.models import Medicine,CartItem

# Register your models here.
admin.site.register(Medicine)
admin.site.register(CartItem)
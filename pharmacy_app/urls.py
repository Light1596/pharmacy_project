from django.urls import path


from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(),name='logout'),
    path('medicines/', views.medicine_list, name='medicine_list'),
    path('medicines/create/', views.medicine_create, name='medicine_create'),
    path('medicines/<int:pk>/update', views.medicine_update, name='medicine_update'),
    path('medicines/<int:pk>/delete', views.medicine_delete, name='medicine_delete')
]
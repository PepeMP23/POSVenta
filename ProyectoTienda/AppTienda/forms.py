from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Store, Product, Promotion

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2')

class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['name', 'description', 'address', 'google_maps_link', 'email', 'image_url']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'category', 'image_url']

class PromotionForm(forms.ModelForm):
    class Meta:
        model = Promotion
        fields = ['product', 'discount', 'start_date', 'end_date']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(PromotionForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['product'].queryset = Product.objects.filter(store__user=user)
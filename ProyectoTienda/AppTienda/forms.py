from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import Product, StockEntry, Sale, Customer, Category
from .validators import validate_corporate_email

User = get_user_model()

# ---- AUTH ----
class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        "class": "form-control",
        "placeholder": "tu@empresa.com"
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        "class": "form-control",
        "placeholder": "********"
    }))

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get("email")
        pwd = cleaned.get("password")
        if email and pwd:
            user = authenticate(username=email, password=pwd)
            if not user:
                raise forms.ValidationError("Credenciales inválidas.")
            cleaned["user"] = user
        return cleaned


# ---- USERS (solo admin/vendor) ----
class BaseUserForm(forms.ModelForm):
    email = forms.EmailField(
        validators=[validate_corporate_email],
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "password",
                  "role", "image_url", "is_staff", "is_active"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name":  forms.TextInput(attrs={"class": "form-control"}),
            "role":       forms.Select(attrs={"class": "form-select"}),
            "image_url":  forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean_password(self):
        pwd = self.cleaned_data.get("password")
        if not self.instance.pk and not pwd:
            raise ValidationError("La contraseña es obligatoria.")
        if pwd:
            validate_password(pwd, self.instance)
        return pwd

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email
        pwd = self.cleaned_data.get("password")
        if pwd:
            user.set_password(pwd)
        if commit:
            user.save()
        return user


class UserForm(BaseUserForm):
    pass


# ---- CUSTOMER (separado de User) ----
class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["first_name", "last_name", "address", "phone"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name":  forms.TextInput(attrs={"class": "form-control"}),
            "address":    forms.TextInput(attrs={"class": "form-control"}),
            "phone":      forms.TextInput(attrs={"class": "form-control"}),
        }


# ---- CATEGORY ----
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description"]
        widgets = {
            "name":        forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


# ---- PRODUCT (con category) ----
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "description", "price", "image_url", "category"]
        widgets = {
            "name":        forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "price":       forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "image_url":   forms.TextInput(attrs={"class": "form-control"}),
            "category":    forms.Select(attrs={"class": "form-select"}),
        }


# ---- STOCK ----
class StockEntryForm(forms.ModelForm):
    class Meta:
        model = StockEntry
        fields = ["product", "quantity", "note"]
        widgets = {
            "product":  forms.Select(attrs={"class": "form-select"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0.01"}),
            "note":     forms.TextInput(attrs={"class": "form-control"}),
        }


# ---- SALE (cliente de tabla Customer) ----
class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        # 👇 ya NO pedimos unit_price
        fields = ["product", "customer", "quantity"]
        widgets = {
            "product":   forms.Select(attrs={"class": "form-select", "id": "id_product"}),
            "customer":  forms.Select(attrs={"class": "form-select"}),
            "quantity":  forms.NumberInput(attrs={"class": "form-control", "step": "1", "min": "1", "id": "id_quantity"}),
        }

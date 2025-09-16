from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator
from decimal import Decimal

# ---------- USER ----------
class UserManager(BaseUserManager):
    use_in_migrations = True
    def _create_user(self, email, password, **extra):
        if not email:
            raise ValueError("El email es obligatorio")
        email = self.normalize_email(email)
        user = self.model(email=email, username=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_user(self, email, password=None, **extra):
        extra.setdefault('is_staff', False)
        extra.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra)
    def create_superuser(self, email, password=None, **extra):
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)
        return self._create_user(email, password, **extra)

class User(AbstractUser):
    """
    Solo roles admin/vendor. El customer es tabla aparte.
    """
    username = models.CharField(max_length=150, blank=True)
    email = models.EmailField(unique=True)
    ROLE_CHOICES = (('admin', 'Admin'), ('vendor', 'Vendor'))
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='vendor')
    created_at = models.DateTimeField(auto_now_add=True)
    image_url = models.CharField(max_length=255, blank=True, default="")
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()
    def __str__(self):  # pragma: no cover
        return f"{self.email} ({self.role})"


# ---------- CUSTOMER (separado de User) ----------
class Customer(models.Model):
    first_name = models.CharField(max_length=150, blank=True, default="")
    last_name  = models.CharField(max_length=150, blank=True, default="")
    address    = models.CharField(max_length=255, blank=True, default="")
    phone      = models.CharField(max_length=30,  blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):  # pragma: no cover
        return f"{self.first_name} {self.last_name}".strip()


# ---------- CATEGORY ----------
class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['name']
    def __str__(self):  # pragma: no cover
        return self.name


# ---------- PRODUCT ----------
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    price = models.FloatField(validators=[MinValueValidator(0.0)])  # DOUBLE
    stock = models.PositiveIntegerField(default=0)  # 👈 entero
    created_at = models.DateTimeField(auto_now_add=True)
    image_url = models.CharField(max_length=255, blank=True, default="")
    category = models.ForeignKey('Category', on_delete=models.PROTECT, null=True, related_name='products')

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.name


# ---------- STOCK ENTRIES (altas de inventario) ----------
class StockEntry(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_entries')
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])  # 👈 entero
    note = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *a, **kw):
        is_new = self.pk is None
        super().save(*a, **kw)
        if is_new:
            self.product.stock = (self.product.stock or 0) + int(self.quantity)
            self.product.save(update_fields=['stock'])

    def __str__(self):
        return f"{self.product} +{self.quantity}"


# ---------- SALE (descuenta stock del producto) ----------
class Sale(models.Model):
    product = models.ForeignKey('Product', on_delete=models.PROTECT, related_name='sales')
    customer = models.ForeignKey('Customer', null=True, blank=True, on_delete=models.SET_NULL, related_name='sales')
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])   # entero
    unit_price = models.FloatField(validators=[MinValueValidator(0.0)])        # se fija desde product
    total_amount = models.FloatField(default=0.0)                               # 👈 nuevo: total guardado
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def total_price(self) -> float:
        # compat: sigue existiendo como propiedad
        return float(self.total_amount)

    def save(self, *args, **kwargs):
        # completa unit_price si no viene (ya no lo pedimos en el form)
        if (self.unit_price is None or self.unit_price == 0) and self.product_id:
            self.unit_price = float(self.product.price)

        # calcula y guarda el total
        self.total_amount = round(float(self.unit_price) * int(self.quantity or 0), 2)

        is_new = self.pk is None
        super().save(*args, **kwargs)

        # descuenta stock solo en la creación
        if is_new:
            prod = self.product
            new_stock = int(prod.stock or 0) - int(self.quantity)
            if new_stock < 0:
                self.delete()
                raise ValueError("Stock insuficiente para esta venta")
            prod.stock = new_stock
            prod.save(update_fields=['stock'])

    def __str__(self):
        return f"Sale #{self.pk} - {self.product} x {self.quantity}"

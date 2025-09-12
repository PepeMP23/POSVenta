from django.contrib import admin
from .models import User, Store, Category, Product, Payment, Orders, OrderItem, Promotion, ShoppingCart, CartItem

admin.site.register(User)
admin.site.register(Store)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Payment)
admin.site.register(Orders)
admin.site.register(OrderItem)
admin.site.register(Promotion)
admin.site.register(ShoppingCart)
admin.site.register(CartItem)
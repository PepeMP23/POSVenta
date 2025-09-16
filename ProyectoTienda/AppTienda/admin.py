from django.contrib import admin
from .models import User, Customer, Category, Product, StockEntry, Sale

admin.site.register(User)
admin.site.register(Customer)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(StockEntry)
admin.site.register(Sale)

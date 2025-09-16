from django.urls import path
from . import views as v
from . import views_category as cat


urlpatterns = [
    path("", v.dashboard, name="index"),
    path("dashboard/", v.dashboard, name="dashboard"),
    path("login/", v.login_view, name="login"),
    path("logout/", v.logout_view, name="logout"),

    # Users
    path("modules/users/", v.users_list, name="users_list"),
    path("modules/users/add/", v.users_add, name="users_add"),
    path("modules/users/<int:pk>/edit/", v.users_edit, name="users_edit"),
    path("modules/users/<int:pk>/delete/", v.users_delete, name="users_delete"),

    # Customers (separados de user)
    path("modules/customers/", v.customers_list, name="customers_list"),
    path("modules/customers/add/", v.customers_add, name="customers_add"),
    path("modules/customers/<int:pk>/edit/", v.customers_edit, name="customers_edit"),
    path("modules/customers/<int:pk>/delete/", v.customers_delete, name="customers_delete"),

    # Categories
    path("modules/categories/", v.categories_list, name="categories_list"),
    path("modules/categories/add/", v.categories_add, name="categories_add"),
    path("modules/categories/<int:pk>/edit/", v.categories_edit, name="categories_edit"),
    path("modules/categories/<int:pk>/delete/", v.categories_delete, name="categories_delete"),

    # Products
    path("modules/products/", v.products_list, name="products_list"),
    path("modules/products/add/", v.products_add, name="products_add"),
    path("modules/products/<int:pk>/edit/", v.products_edit, name="products_edit"),
    path("modules/products/<int:pk>/delete/", v.products_delete, name="products_delete"),

    # Stock
    path("modules/stock/", v.stock_list, name="stock_list"),
    path("modules/stock/add/", v.stock_add, name="stock_add"),
    path("modules/stock/<int:pk>/delete/", v.stock_delete, name="stock_delete"),

    # Sales
    path("modules/sales/", v.sales_list, name="sales_list"),
    path("modules/sales/add/", v.sales_add, name="sales_add"),
    path("modules/sales/<int:pk>/delete/", v.sales_delete, name="sales_delete"),

    # Categories
    path("modules/categories/", cat.categories_list, name="categories_list"),
    path("modules/categories/add/", cat.categories_add, name="categories_add"),
    path("modules/categories/<int:pk>/edit/", cat.categories_edit, name="categories_edit"),
    path("modules/categories/<int:pk>/delete/", cat.categories_delete, name="categories_delete"),
]


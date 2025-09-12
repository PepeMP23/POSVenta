from django.urls import path
from django.conf.urls import handler404
from . import views

handler404 = 'AppTienda.views.error_404_view'

urlpatterns = [
    path("", views.store_list, name="index"),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('vendorHome/', views.vendorHome, name='vendorHome'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('buy_now/<int:product_id>/', views.buy_now, name='buy_now'),
    path('manage_store/', views.manage_store, name='manage_store'),
    path('vendor/products/', views.vendor_products, name='vendor_products'),
    path('vendor/products/create/', views.create_product, name='create_product'),
    path('vendor/profile/', views.vendor_profile, name='vendor_profile'),
    path('cart/', views.cart_view, name='cart'),
    path('checkout/', views.checkout_views, name='checkout'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, {'remove_all': True}, name='remove_from_cart'),
    path('cart/removes/<int:item_id>/', views.remove_from_carts, {'remove_all': False}, name='remove_from_carts'),
    path('order-history/', views.order_history, name='order_history'),
    path('profile/', views.profile_view, name='profile'),
    path('store/<int:store_id>/', views.store_view, name='store_view'),
    path('sales_history/', views.sales_history_view, name='sales_history'),
    path('add_promotion/', views.add_promotion, name='add_promotion'),
    path('list_promotions/', views.list_promotions, name='list_promotions'),
    path('products_with_offers/', views.products_with_offers, name='products_with_offers'),
    path('search_stores/', views.search_stores, name='search_stores'),
    path('product/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    
    # path('order_success/', views.order_success, name='order_success'),
    



    
]

# http://127.0.0.1:8000/tienda/product/1/

urlpatterns += [
    path('accounts/login/', views.login_view),  # Redirige a la vista personalizada
]
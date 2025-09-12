from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm, StoreForm, ProductForm, PromotionForm
from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect
from .models import ShoppingCart, CartItem, Product, Store, Orders, OrderItem, Payment, Promotion, Category, Orders, OrderItem
from datetime import datetime, timedelta
from django.db.models import Q
from unidecode import unidecode
from .models import Store
from .decorators import user_passes_test_404
from django.contrib import messages

def user_is_customer(user):
    return user.role == 'customer'

def user_is_vendor(user):
    return user.role == 'vendor'

def user_is_admin(user):
    return user.role == 'admin'

def register(request):
    if request.user.is_authenticated:
        return redirect('/')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            if user.role == 'vendor':
                return redirect('vendorHome')
            else:
                return redirect('index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'AppTienda/registration/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('/')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if user.role == 'vendor':
                    return redirect('vendorHome')
                else:
                    return redirect('/')
    else:
        form = AuthenticationForm()
    return render(request, 'AppTienda/registration/login.html', {'form': form})
# General Access

def store_list(request):
    stores = Store.objects.all()
    products = [store.product_set.first() for store in stores]
    return render(request, 'AppTienda/store/store_list.html', {'stores': stores, 'products': products})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'AppTienda/store/product_detail.html', {'product': product})


# Vendor Access Required ONLY
@login_required
@user_passes_test_404(user_is_vendor)
def manage_store(request):
    try:
        store = Store.objects.get(user=request.user)
        if request.method == 'POST':
            form = StoreForm(request.POST, request.FILES, instance=store)
            if form.is_valid():
                form.save()
                return redirect('vendorHome')
        else:
            form = StoreForm(instance=store)
    except Store.DoesNotExist:
        if request.method == 'POST':
            form = StoreForm(request.POST, request.FILES)
            if form.is_valid():
                new_store = form.save(commit=False)
                new_store.user = request.user
                new_store.save()
                return redirect('vendorHome')
        else:
            form = StoreForm()

    return render(request, 'AppTienda/store/manage_store.html', {'form': form})

 
@login_required
@user_passes_test_404(user_is_vendor)
def vendor_products(request):
    try:
        store = Store.objects.get(user=request.user)
        products = Product.objects.filter(store=store)
    except Store.DoesNotExist:
        return redirect('manage_store')  # Redirige al usuario para que cree su tienda primero

    return render(request, 'AppTienda/store/vendor_products.html', {'products': products})

@login_required
@user_passes_test_404(user_is_vendor)
def create_product(request):
    try:
        store = Store.objects.get(user=request.user)
    except Store.DoesNotExist:
        return redirect('manage_store')  # Redirige al usuario para que cree su tienda primero

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.store = store
            product.save()
            return redirect('vendor_products')
    else:
        form = ProductForm()

    categories = Category.objects.all()

    return render(request, 'AppTienda/store/create_product.html', {'form': form, 'categories': categories})

@login_required
@user_passes_test_404(user_is_vendor)
def vendor_profile(request):
    user = request.user
    try:
        store = Store.objects.get(user=user)
    except Store.DoesNotExist:
        store = None

    context = {
        'user': user,
        'store': store,
    }
    return render(request, 'AppTienda/store/vendor_profile.html', context)

# Only customer can access, login is required
@login_required
@user_passes_test_404(user_is_customer)
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = ShoppingCart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
    cart_item.save()
    return redirect('product_detail', product_id=product_id)

@login_required
@user_passes_test_404(user_is_customer)
def buy_now(request, product_id):
    add_to_cart(request, product_id)
    return redirect(checkout_views)

@login_required
@user_passes_test_404(user_is_customer)
def checkout_views(request):
    cart, created = ShoppingCart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    total_price = sum(item.product.price * item.quantity for item in cart_items)
    
    # Agregar promoción a cada item del carrito
    for item in cart_items:
        item.promotion = Promotion.objects.filter(product=item.product).first()

    if request.method == "POST":
        insufficient_stock_items = []
        for item in cart_items:
            if item.quantity > item.product.stock:
                insufficient_stock_items.append(item)

        if insufficient_stock_items:
            for item in insufficient_stock_items:
                messages.error(request, f"Stock insuficiente para {item.product.name}. Disponible: {item.product.stock}")
            return render(request, 'AppTienda/checkout.html', {'cart_items': cart_items, 'total_price': total_price})
        address = request.POST['address']
        card_number = request.POST['card_number']
        payment_type = request.POST['payment_type']

        payment = Payment.objects.create(payment_type=payment_type, card_number=card_number[-4:])
        order = Orders.objects.create(customer=request.user, payment=payment, address=address, total_price=total_price)
        
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                store=item.product.store,
                quantity=item.quantity,
                price=item.product.price,
                promotion=item.promotion,
                shipping_date=datetime.now() + timedelta(days=3)
            )
            item.product.stock -= item.quantity
            item.product.save()
            item.delete()
        cart.delete()

        return render(request, 'AppTienda/store/order_success.html')

    return render(request, 'AppTienda/store/checkout.html', {'cart_items': cart_items, 'total_price': total_price})
@login_required
@user_passes_test_404(user_is_customer)
def cart_view(request):
    cart, created = ShoppingCart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    total_price = sum(item.product.price * item.quantity for item in cart_items)
    total_products = sum(item.quantity for item in cart_items)
    # Agregar promoción a cada item del carrito
    for item in cart_items:
        item.promotion = Promotion.objects.filter(product=item.product).first()

    
    return render(request, 'AppTienda/store/cart.html', {'cart_items': cart_items, 'total_price': total_price, 'total_products': total_products})
@login_required
@user_passes_test_404(user_is_customer)
def remove_from_cart(request, item_id, remove_all=False):
    cart_item = get_object_or_404(CartItem, id=item_id)
    if remove_all==True or cart_item.quantity == 1:
        cart_item.delete()
    else:
        cart_item.quantity -= 1
        cart_item.save()
    return redirect('cart')
@login_required
@user_passes_test_404(user_is_customer)
def remove_from_carts(request, item_id, remove_all=False):
    cart_item = get_object_or_404(CartItem, id=item_id)
    if remove_all==True or cart_item.quantity == 1:
        cart_item.delete()
    else:
        cart_item.quantity -= 1
        cart_item.save()
    return redirect('cart')
@login_required
@user_passes_test_404(user_is_customer)
def order_history(request):
    orders = Orders.objects.filter(customer=request.user).order_by('-order_date')
    
    orders_data = []
    for order in orders:
        order_items = OrderItem.objects.filter(order=order)
        orders_data.append({
            'order': order,
            'items': order_items
        })

    return render(request, 'AppTienda/store/order_history.html', {'orders_data': orders_data})
@login_required
def profile_view(request):
    user = request.user  # Obtener el usuario actual
    
    return render(request, 'AppTienda/store/profile.html', {'user': user})

def store_view(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    products = Product.objects.filter(store=store)

    context = {
        'store': store,
        'products': products
    }

    return render(request, 'AppTienda/store/store_view.html', context)

@login_required
@user_passes_test_404(user_is_vendor)
def sales_history_view(request):
    try:
        store = Store.objects.get(user=request.user)
        # Filtrar los OrderItem que pertenecen a la tienda del usuario
        order_items = OrderItem.objects.filter(store=store)

        orders_data = {}
        for item in order_items:
            order_id = item.order.id
            if order_id not in orders_data:
                orders_data[order_id] = {
                    'order_date': item.order.order_date,
                    'total_price': 0,
                    'payment_type': item.order.payment.payment_type,
                    'items': []
                }
            orders_data[order_id]['total_price'] += item.price * item.quantity
            orders_data[order_id]['items'].append(item)
        
    except Store.DoesNotExist:
        return redirect('manage_store')  # Redirige al usuario para que cree su tienda primero
    
    return render(request, 'AppTienda/store/sales_history.html', {'orders_data': orders_data.values()})

@login_required
@user_passes_test_404(user_is_vendor)
def add_promotion(request):
    store = Store.objects.get(user=request.user)
    if request.method == 'POST':
        form = PromotionForm(request.POST, user=request.user)
        if form.is_valid():
            promotion = form.save()
            # Actualizar el precio del producto
            product = promotion.product
            original_price = product.price
            discount = promotion.discount / 100
            product.price = original_price * (1 - discount)
            product.save()
            return redirect('list_promotions')
    else:
        form = PromotionForm(user=request.user)
    return render(request, 'AppTienda/store/add_promotion.html', {'form': form})

@login_required
@user_passes_test_404(user_is_vendor)
def list_promotions(request):
    store = Store.objects.get(user=request.user)
    promotions = Promotion.objects.filter(product__store=store)

    if request.method == 'POST':
        promotion_id = request.POST.get('promotion_id')
        if promotion_id:
            promotion = Promotion.objects.get(id=promotion_id)
            product = promotion.product
            discount = promotion.discount / 100
            original_price = product.price / (1 - discount)
            product.price = original_price
            product.save()
            promotion.delete()
            return redirect('list_promotions')

    return render(request, 'AppTienda/store/list_promotions.html', {'promotions': promotions})

def products_with_offers(request):
    promotions = Promotion.objects.all()
    return render(request, 'AppTienda/store/products_with_offers.html', {'promotions': promotions})



def search_stores(request):
    query = request.GET.get('q', '')
    normalized_query = unidecode(query).lower()
    
    stores = Store.objects.filter(
        Q(name__icontains=normalized_query) |
        Q(name__icontains=query)
    )
    
    return render(request, 'AppTienda/store/search_results.html', {'stores': stores, 'query': query})

def error_404_view(request, exception=None):
    return render(request, 'AppTienda/404.html', {})


@login_required
@user_passes_test(user_is_vendor, login_url='login')
def vendorHome(request):
    try:
        # Obtener la tienda del usuario vendedor actual
        store = Store.objects.get(user=request.user)
    except Store.DoesNotExist:
        # Manejar el caso en que la tienda no exista
        store = None
    
    context = {
        'user': request.user,
        'store': store,
    }

    return render(request, 'AppTienda/store/vendorHome.html', context)

@login_required
@user_passes_test_404(user_is_vendor)
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    store = product.store

    if store.user != request.user:
        return HttpResponseForbidden("No tienes permiso para editar este producto.")

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('vendor_products')
    else:
        form = ProductForm(instance=product)

    categories = Category.objects.all()

    return render(request, 'AppTienda/store/edit_product.html', {'form': form, 'categories': categories, 'product': product})
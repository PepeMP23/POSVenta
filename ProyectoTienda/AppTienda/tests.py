from django.test import TestCase, Client
from django.urls import reverse
from AppTienda.models import User, Product, Store, ShoppingCart, CartItem, Category

class ShoppingCartTestCase(TestCase):
    def setUp(self):
        # Create a vendor user and store
        self.vendor_user = User.objects.create_user(username='vendor', password='password', role='vendor', email='vendor@example.com')
        self.store = Store.objects.create(name='Test Store', user=self.vendor_user, address='Test Address', email='store@example.com')

        # Create a category
        self.category = Category.objects.create(name='Test Category')

        # Create a product
        self.product = Product.objects.create(name='Test Product', price=10.0, stock=100, store=self.store, category=self.category)

        # Create a customer user
        self.customer = User.objects.create_user(username='customer', password='password', role='customer', email='customer@example.com')

        # Create a client
        self.client = Client()

    def test_add_product_to_cart(self):
        # Log in as the customer
        login = self.client.login(username='customer', password='password')
        self.assertTrue(login)

        # Add the product to the cart
        response = self.client.post(reverse('add_to_cart', args=[self.product.id]))
        self.assertEqual(response.status_code, 302)  # Redirects to product detail page

        # Check if the product is in the cart
        cart = ShoppingCart.objects.get(user=self.customer)
        cart_item = CartItem.objects.get(cart=cart, product=self.product)
        self.assertEqual(cart_item.quantity, 1)

        # Print to see the result in the console (optional)
        print("Test passed: Product added to cart successfully.")
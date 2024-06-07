from django.test import TestCase

from django.test import TestCase
from django_redis import get_redis_connection
from .cart import Cart  # Adjust the import as necessary based on your project structure.


# Create your tests here.

class CartTestCase(TestCase):
    def setUp(self):
        # Set up initial conditions for tests
        self.user_id = 'testuser_1'
        self.cart = Cart(self.user_id)

        # Ensure the cart is empty at the beginning of each test
        redis_conn = get_redis_connection("default")
        redis_conn.delete(self.cart.cart_key)

    def test_add_to_cart(self):
        self.cart.add_to_cart('americano', 1)
        cart_data = self.cart.get_cart()
        self.assertEqual(int(cart_data[b'americano']), 1, "Failed to add item to cart")

    def test_update_quantity(self):
        self.cart.add_to_cart('americano', 1)
        self.cart.update_quantity('americano', 2)
        cart_data = self.cart.get_cart()
        self.assertEqual(int(cart_data[b'americano']), 3, "Failed to update item quantity")

    def test_remove_from_cart(self):
        self.cart.add_to_cart('americano', 1)
        self.cart.remove_from_cart('americano')
        cart_data = self.cart.get_cart()
        self.assertFalse(b'americano' in cart_data, "Failed to remove item from cart")

    def test_get_cart(self):
        self.cart.add_to_cart('americano', 1)
        self.cart.add_to_cart('latte', 2)
        cart_data = self.cart.get_cart()
        self.assertEqual(int(cart_data[b'americano']), 1, "Failed to fetch correct item quantity for 'americano'")
        self.assertEqual(int(cart_data[b'latte']), 2, "Failed to fetch correct item quantity for 'latte'")

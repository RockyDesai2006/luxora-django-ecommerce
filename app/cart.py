from .models import Product

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')

        if not cart:
            cart = self.session['cart'] = {}

        self.cart = cart

    def add(self, product):
        product_id = str(product.id)

        if product_id not in self.cart:
            self.cart[product_id] = {
                'name': product.name,
                'price': float(product.price),
                'qty': 1,
                'image': product.image.url
            }
        else:
            self.cart[product_id]['qty'] += 1

        self.save()

    def remove(self, product_id):
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self):
        self.session['cart'] = {}
        self.save()

    def save(self):
        self.session.modified = True

    def total_price(self):
        return sum(item['price'] * item['qty'] for item in self.cart.values())

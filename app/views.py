from .cart import Cart
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Product, Review
from .models import Order, OrderItem

@login_required(login_url='login')

def add_to_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.add(product)
    return redirect('shop')

def remove_from_cart(request, product_id):
    cart = Cart(request)
    cart.remove(product_id)
    return redirect('cart')

def cart_view(request):
    cart = Cart(request)
    return render(request, 'cart.html', {'cart': cart.cart, 'total': cart.total_price()})

def home(request):
    products = Product.objects.filter(is_active=True)
    return render(request, 'home.html', {'products': products})

def shop(request):
    products = Product.objects.filter(is_active=True)
    return render(request, 'shop.html', {'products': products})

def collections(request):
    return render(request, 'collections.html')

def about(request):
    return render(request, 'about.html')

# ---------- REGISTER ----------
def register_view(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=email).exists():
            messages.error(request, "User already exists")
            return redirect('login')

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name
        )
        user.save()

        messages.success(request, "Account created successfully")
        return redirect('login')

    return redirect('login')

# ---------- LOGIN ----------
def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(username=email, password=password)

        if user is not None:
            login(request, user)  # SESSION CREATED HERE
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials")
            return redirect('login')

    return render(request, 'login.html')

# ---------- LOGOUT ----------
def logout_view(request):
    logout(request)  # SESSION DESTROYED
    return redirect('login')

#--------------Single Product Page------------------
def product_detail(request, id):
    product = Product.objects.get(id=id)
    reviews = product.reviews.all()

    similar_products = Product.objects.filter(
        category=product.category
    ).exclude(id=id)[:4]

    # Handle review submission
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect('login')

        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        Review.objects.create(
            product=product,
            user=request.user,
            rating=rating,
            comment=comment
        )
        return redirect('product_detail', id=id)

    return render(request, 'product.html', {
        'product': product,
        'reviews': reviews,
        'similar_products': similar_products
    })


@login_required(login_url='login')
def checkout(request):
    cart = Cart(request)

    if not cart.cart:
        return redirect('shop')

    if request.method == "POST":
        order = Order.objects.create(
            user=request.user,
            full_name=request.POST['full_name'],
            email=request.POST['email'],
            address=request.POST['address'],
            city=request.POST['city'],
            postal_code=request.POST['postal_code'],
            total_amount=cart.total_price()
        )

        for product_id, item in cart.cart.items():
            OrderItem.objects.create(
                order=order,
                product_id=product_id,
                price=item['price'],
                quantity=item['qty']
            )

        cart.clear()
        return redirect('order_success')

    return render(request, 'checkout.html', {
        'cart': cart.cart,
        'total': cart.total_price()
    })

def order_success(request):
    return render(request, 'order_success.html')

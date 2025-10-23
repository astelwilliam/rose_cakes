from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.mail import send_mail
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Cake, Order, OrderItem, Category, Coupon, SpecialOffer
import razorpay
# import stripe    # Uncomment when installing stripe

def homepage(request):
    featured_cakes = Cake.objects.filter(featured=True)
    special_offers = SpecialOffer.objects.filter(active=True, valid_from__lte=timezone.now(), valid_until__gte=timezone.now())
    return render(request, 'rose_cakes/homepage.html', {'featured_cakes': featured_cakes, 'special_offers': special_offers})

def catalog(request):
    category_id = request.GET.get('category', '')

    cakes = Cake.objects.all()

    # Filter by category if selected
    if category_id:
        cakes = cakes.filter(category_id=category_id)

    # Sort cakes by category name, then cake name
    cakes = cakes.order_by('category__name', 'name')

    categories = Category.objects.all().order_by('name')

    return render(request, 'rose_cakes/catalog.html', {
        'cakes': cakes,
        'categories': categories,
        'selected_category': category_id
    })

def cake_detail(request, cake_id):
    cake = get_object_or_404(Cake, id=cake_id)
    return render(request, 'rose_cakes/cake_detail.html', {'cake': cake})

def add_to_cart(request, cake_id):
    cake = get_object_or_404(Cake, id=cake_id)
    cart = request.session.get('cart', {})

    if str(cake_id) in cart:
        cart[str(cake_id)] += 1
    else:
        cart[str(cake_id)] = 1

    request.session['cart'] = cart
    messages.success(request, f'{cake.name} added to cart!')
    return redirect('cake_detail', cake_id=cake_id)

def buy_now(request, cake_id):
    cake = get_object_or_404(Cake, id=cake_id)
    # Clear cart and add only this item
    request.session['cart'] = {str(cake_id): 1}
    messages.success(request, f'{cake.name} added to cart. Proceeding to checkout...')
    return redirect('checkout')

def remove_from_cart(request, cake_id):
    cart = request.session.get('cart', {})
    cake = get_object_or_404(Cake, id=cake_id)

    if str(cake_id) in cart:
        if cart[str(cake_id)] > 1:
            cart[str(cake_id)] -= 1
        else:
            del cart[str(cake_id)]

    request.session['cart'] = cart
    messages.success(request, f'{cake.name} removed from cart!')
    return redirect('cart')

def cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    total_items = 0

    for cake_id, quantity in cart.items():
        cake = get_object_or_404(Cake, id=cake_id)
        subtotal = cake.price * quantity
        total += subtotal
        total_items += quantity
        cart_items.append({
            'cake': cake,
            'quantity': quantity,
            'subtotal': subtotal,
            'total_price': subtotal  # Added for template compatibility
        })

    # Calculate delivery charge
    delivery_charge = 100
    final_total = total + delivery_charge

    return render(request, 'rose_cakes/cart.html', {
        'cart': cart_items,  # Changed to 'cart' for template compatibility
        'cart_items': cart_items,
        'total': total,
        'total_items': total_items,
        'total_price': total,  # Added for template compatibility
        'delivery_charge': delivery_charge,
        'final_total': final_total
    })

def checkout(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for cake_id, quantity in cart.items():
        cake = get_object_or_404(Cake, id=cake_id)
        subtotal = cake.price * quantity
        total += subtotal
        cart_items.append({
            'cake': cake,
            'quantity': quantity,
            'subtotal': subtotal
        })

    # Calculate delivery charge
    delivery_charge = 0 if total >= 1000 else 100
    final_total = total + delivery_charge

    # Check for special offers
    special_offer_discount = 0
    applied_offer = None
    if total > 0:  # Apply offers if cart has items
        active_offers = SpecialOffer.objects.filter(active=True, valid_from__lte=timezone.now(), valid_until__gte=timezone.now())
        for offer in active_offers:
            if total >= offer.minimum_order_value:
                discount = offer.get_discount_amount(total)
                if discount > special_offer_discount:
                    special_offer_discount = discount
                    applied_offer = offer

    final_total = total - special_offer_discount + delivery_charge

    if request.method == 'POST':
        if not cart:
            messages.error(request, 'Your cart is empty!')
            return redirect('cart')

        customer_name = request.POST.get('name')
        customer_email = request.POST.get('email')
        customer_address = request.POST.get('address')
        customer_pincode = request.POST.get('pincode')

        # Validate delivery area (only pincode 682001 or within 5km)
        if customer_pincode != '682001':
            messages.error(request, 'Sorry, we only deliver within 5km radius of our location (Pincode: 682001).')
            return redirect('checkout')

        # Apply coupon if provided
        coupon_code = request.POST.get('coupon_code')
        discount = 0
        coupon = None
        if coupon_code:
            try:
                coupon = Coupon.objects.get(
                    code=coupon_code.upper(),
                    active=True,
                    valid_from__lte=timezone.now(),
                    valid_until__gte=timezone.now(),
                    used_count__lt=models.F('usage_limit')
                )
                discount = total * (coupon.discount_percentage / 100)
                coupon.used_count += 1
                coupon.save()
            except Coupon.DoesNotExist:
                messages.error(request, 'Invalid or expired coupon code!')
                return redirect('checkout')

        final_total = total - discount - special_offer_discount + delivery_charge

        # Create Razorpay order (mock for testing)
        # client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        # razorpay_order = client.order.create({
        #     'amount': int(final_total * 100),  # Amount in paisa
        #     'currency': 'INR',
        #     'payment_capture': '1'
        # })

        # Create order first to get ID for mock payment
        order = Order.objects.create(
            customer_name=customer_name,
            customer_email=customer_email,
            customer_address=customer_address,
            total_amount=final_total,
            user=request.user if request.user.is_authenticated else None,
            coupon=coupon,
            special_offer=applied_offer,
            discount_amount=discount + special_offer_discount,
            payment_id='temp'  # Temporary value, will be updated
        )

        # Mock Razorpay order for testing
        razorpay_order = {
            'id': f'order_mock_{order.id}',
            'amount': int(final_total * 100),
            'currency': 'INR'
        }

        # Update payment_id with correct order.id
        order.payment_id = razorpay_order['id']
        order.save()

        for cake_id, quantity in cart.items():
            cake = get_object_or_404(Cake, id=cake_id)
            price = cake.price

            OrderItem.objects.create(
                order=order,
                cake=cake,
                quantity=quantity,
                price=price
            )

        # Clear cart
        request.session['cart'] = {}

        return render(request, 'rose_cakes/checkout.html', {
            'cart_items': cart_items,
            'total': final_total,
            'delivery_charge': delivery_charge,
            'special_offer_discount': special_offer_discount,
            'applied_offer': applied_offer,
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'customer_name': customer_name,
            'customer_email': customer_email,
            'order_id': order.id
        })

    return render(request, 'rose_cakes/checkout.html', {
        'cart_items': cart_items,
        'total': total,
        'delivery_charge': delivery_charge,
        'final_total': final_total,
        'special_offer_discount': special_offer_discount,
        'applied_offer': applied_offer
    })

def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Add subtotal to each order item for template display
    for item in order.items.all():
        item.subtotal = item.price * item.quantity

    return render(request, 'rose_cakes/order_confirmation.html', {'order': order})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'rose_cakes/order_history.html', {'orders': orders})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('homepage')
    else:
        form = UserCreationForm()
    return render(request, 'rose_cakes/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('homepage')
        else:
            messages.error(request, 'Invalid credentials!')
    return render(request, 'rose_cakes/login.html')

def user_logout(request):
    logout(request)
    return redirect('homepage')

def search(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')

    cakes = Cake.objects.all()

    if query:
        cakes = cakes.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

    if category_id:
        cakes = cakes.filter(category_id=category_id)

    categories = Category.objects.all()

    return render(request, 'rose_cakes/search.html', {
        'cakes': cakes,
        'query': query,
        'categories': categories,
        'selected_category': category_id
    })

def apply_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        try:
            coupon = Coupon.objects.get(
                code=coupon_code.upper(),
                active=True,
                valid_from__lte=timezone.now(),
                valid_until__gte=timezone.now(),
                used_count__lt=models.F('usage_limit')
            )
            request.session['coupon_code'] = coupon.code
            messages.success(request, f'Coupon {coupon.code} applied! {coupon.discount_percentage}% discount.')
        except Coupon.DoesNotExist:
            messages.error(request, 'Invalid or expired coupon code!')
    return redirect('cart')

@csrf_exempt
def payment_success(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_signature = data.get('razorpay_signature')

        # For testing purposes, skip signature verification and mock success
        # In production, uncomment the code below to verify signatures
        # client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        # params_dict = {
        #     'razorpay_order_id': razorpay_order_id,
        #     'razorpay_payment_id': razorpay_payment_id,
        #     'razorpay_signature': razorpay_signature
        # }

        try:
            # Mock verification for testing - always succeed
            # client.utility.verify_payment_signature(params_dict)
            # Payment verified successfully
            order = Order.objects.get(payment_id=razorpay_order_id)
            order.status = 'confirmed'
            order.save()

            # Send confirmation email
            try:
                send_mail(
                    'Payment Successful - Rose Cakes',
                    f'Thank you for your payment! Order #{order.id} has been confirmed.\n\nTotal: ₹{order.total_amount:.2f}\n\nWe will process your order soon.',
                    settings.EMAIL_HOST_USER,
                    [order.customer_email],
                    fail_silently=True,
                )
            except:
                pass

            return JsonResponse({'status': 'success'})
        except:
            return JsonResponse({'status': 'failed'})

    return JsonResponse({'status': 'invalid'})

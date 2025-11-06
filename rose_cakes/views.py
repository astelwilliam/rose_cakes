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
from .models import Cake, Order, OrderItem, Category, Coupon, SpecialOffer, SiteSettings
from .notifications import notify_admin_new_order, notify_user_order_status
from django.urls import reverse
from django.template.loader import render_to_string
from difflib import SequenceMatcher
# import razorpay # Removed Razorpay
# import stripe    # Uncomment when installing stripe

def homepage(request):
    featured_cakes = Cake.objects.filter(featured=True)
    special_offers = SpecialOffer.objects.filter(active=True, valid_from__lte=timezone.now(), valid_until__gte=timezone.now())
    site_settings = SiteSettings.get_settings()
    return render(request, 'rose_cakes/homepage.html', {'featured_cakes': featured_cakes, 'special_offers': special_offers, 'site_settings': site_settings})

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
    
    # If AJAX request, return JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        total_items = sum(cart.values())
        return JsonResponse({
            'success': True,
            'message': f'{cake.name} added to cart!',
            'total_items': total_items
        })
    
    messages.success(request, f'{cake.name} added to cart!')
    return redirect('cart')

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

    return render(request, 'rose_cakes/cart.html', {
        'cart': cart_items,  # Changed to 'cart' for template compatibility
        'cart_items': cart_items,
        'total': total,
        'total_items': total_items,
        'total_price': total,  # Added for template compatibility
        'final_total': total
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

    final_total = total

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

    final_total = total - special_offer_discount

    if request.method == 'POST':
        if not cart:
            messages.error(request, 'Your cart is empty!')
            return redirect('cart')

        customer_name = request.POST.get('name')
        customer_email = request.POST.get('email')
        whatsapp_number = request.POST.get('whatsapp_number')
        pickup_date_str = request.POST.get('pickup_date')
        
        try:
            pickup_date = timezone.datetime.strptime(pickup_date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            messages.error(request, 'Invalid pickup date format.')
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

        final_total = total - discount - special_offer_discount

        order = Order.objects.create(
            customer_name=customer_name,
            customer_email=customer_email,
            whatsapp_number=whatsapp_number,
            pickup_date=pickup_date,
            total_amount=final_total,
            user=request.user if request.user.is_authenticated else None,
            coupon=coupon,
            special_offer=applied_offer,
            discount_amount=discount + special_offer_discount,
            status='pending' # Await admin acceptance
        )

        for cake_id, quantity in cart.items():
            cake = get_object_or_404(Cake, id=cake_id)
            price = cake.price

            OrderItem.objects.create(
                order=order,
                cake=cake,
                quantity=quantity,
                price=price
            )

        # Notify admin of new order
        try:
            notify_admin_new_order(order)
        except Exception:
            pass

        # Clear cart
        request.session['cart'] = {}

        return redirect('order_confirmation', order_id=order.id)

    return render(request, 'rose_cakes/checkout.html', {
        'cart_items': cart_items,
        'total': total,
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

def search_suggestions(request):
    q = request.GET.get('q', '').strip()
    category_id = request.GET.get('category') or ''
    suggestions = []
    if q:
        base_qs = Cake.objects.all()
        if category_id:
            base_qs = base_qs.filter(category_id=category_id)
        exact_first = list(base_qs.filter(name__istartswith=q)[:5])
        contains_next = list(base_qs.filter(name__icontains=q).exclude(id__in=[c.id for c in exact_first])[:5])
        by_category = list(base_qs.filter(category__name__icontains=q).exclude(id__in=[c.id for c in exact_first + contains_next])[:5])
        combined = exact_first + contains_next + by_category

        if not combined:
            # Fuzzy fallback using simple similarity
            names = list(base_qs.values('id', 'name'))
            scored = []
            for item in names:
                ratio = SequenceMatcher(None, q.lower(), item['name'].lower()).ratio()
                if ratio >= 0.5:
                    scored.append((ratio, item['id'], item['name']))
            scored.sort(reverse=True)
            for _, cid, cname in scored[:5]:
                suggestions.append({
                    'id': cid,
                    'name': cname,
                    'detail_url': reverse('cake_detail', args=[cid])
                })
        else:
            for cake in combined[:5]:
                suggestions.append({
                    'id': cake.id,
                    'name': cake.name,
                    'detail_url': reverse('cake_detail', args=[cake.id])
                })

    return JsonResponse({'suggestions': suggestions})

def search_results(request):
    q = request.GET.get('q', '').strip()
    category_id = request.GET.get('category') or ''
    cakes = Cake.objects.all()
    if category_id:
        cakes = cakes.filter(category_id=category_id)
    if q:
        cakes = cakes.filter(
            Q(name__icontains=q) | Q(description__icontains=q) | Q(category__name__icontains=q)
        )
    cakes = cakes.order_by('name')

    html = render_to_string('rose_cakes/partials/search_results.html', {
        'cakes': cakes,
    }, request=request)
    return JsonResponse({'html': html, 'count': cakes.count()})

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

def privacy_policy(request):
    return render(request, 'rose_cakes/privacy_policy.html')

def terms_conditions(request):
    return render(request, 'rose_cakes/terms_conditions.html')

import json
from locale import currency
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from .models import Product, Category,Order
from .serializers import ProductSerializer
from django.views.generic import DetailView
from rest_framework import status
from rest_framework.generics import ListAPIView
from django.views.generic import TemplateView
from django.views import View
from django.http import JsonResponse
import requests
import stripe
from django.conf import settings
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.core.mail import EmailMultiAlternatives
import stripe

def main(request: HttpRequest) -> HttpResponse:
    return render(request, 'main.html')

def stripe_success(request):
    return redirect('/?payment=success')
def stripe_cancel(request):
    return(redirect('/?payment=cancel'))

class ShopPageView(TemplateView):
    template_name = 'shop.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

class ProductListAPIView(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all()
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug' 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['gallery'] = self.object.gallery.all() 
        return context
    
    
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    gallery = product.gallery_images.all()  
    return render(request, 'users/product_detail.html', {
        'product': product,
        'gallery': gallery,
    })
    
class ConvertPriceView(View):
    def get(self, request):
        price_eur = float(request.GET.get("price_eur", 0))
        currency = request.GET.get("currency", "USD").upper()

        response = requests.get("https://api.frankfurter.app/latest?from=EUR")
        data = response.json()
        rate = data["rates"].get(currency)
        if currency == "EUR":
            rate = 1
        else:
            rate = data["rates"].get(currency)

        if rate:
            converted_price = round(price_eur * rate, 2)
            return JsonResponse({"price": converted_price, "currency": currency})

        return JsonResponse({"error": "Invalid currency"}, status=400)
    
    stripe.api_key = settings.STRIPE_SECRET_KEY 
    
@csrf_exempt
@require_POST
def create_checkout_session(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    
    try:
        data = json.loads(request.body) 
        quantity = int(data.get("quantity", 1))
    except Exception:
        quantity = 1

    if quantity < 1:
        quantity = 1

    
    unit_amount = int(product.price * 100)

    
    order = Order.objects.create(product=product, quantity=quantity)

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "eur",
                    "product_data": {"name": product.name},
                    "unit_amount": unit_amount,
                },
                "quantity": quantity,  
            }],
            mode="payment",
            success_url=settings.DOMAIN + reverse("stripe_success") + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=settings.DOMAIN + reverse("stripe_cancel"),
            metadata={"order_id": str(order.id)},
            shipping_address_collection={
                "allowed_countries": [
                    "AT","BE","BG","HR","CY","CZ","DK","EE","FI","FR","DE","GR","HU","IE","IT",
                    "LV","LT","LU","MT","NL","PL","PT","RO","SK","SI","ES","SE","UA",
                ],
            },
        )
        order.stripe_session_id = checkout_session.id
        order.save()
        return JsonResponse({"url": checkout_session.url})
    except Exception as e:
        return JsonResponse({"error": str(e)})


def send_order_email(order):
    subject = f"Подтверждение заказа #{order.id}"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [order.email]

    text_content = (
        f"Здравствуйте!\n\n"
        f"Ваш заказ #{order.id} успешно оплачен.\n"
        f"Товар: {order.product.name}\n"
        f"Количество: {order.quantity}\n"
        f"Сумма: {order.product.price * order.quantity} EUR\n\n"
        f"Спасибо за покупку!"
    )

    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
        <div style="max-width: 600px; margin: auto; background-color: white; padding: 20px; border-radius: 8px;">
            <h2 style="color: #4CAF50;">Спасибо за покупку!</h2>
            <p>Здравствуйте!</p>
            <p>Ваш заказ <strong>#{order.id}</strong> успешно оплачен.</p>
            <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Товар</strong></td>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">{order.product.name}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Количество</strong></td>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">{order.quantity}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Сумма</strong></td>
                    <td style="padding: 8px; border-bottom: 1px solid #ddd;">{order.product.price * order.quantity} EUR</td>
                </tr>
            </table>
            <p style="margin-top: 20px;">Мы скоро отправим ваш товар!</p>
        </div>
    </body>
    </html>
    """

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        order_id = session.get('metadata', {}).get('order_id')
        customer_email = session.get('customer_details', {}).get('email')

        if order_id:
            for order_id in order_id.split(','):
                try:
                    order = Order.objects.get(pk=order_id)
                    order.status = 'paid'

                    
                    if customer_email:
                        order.email = customer_email

                    
                    shipping = session.get('shipping', None)
                    if shipping:
                        address = shipping.get('address', {})
                        order.shipping_name = shipping.get('name', '')
                        order.shipping_line1 = address.get('line1', '')
                        order.shipping_line2 = address.get('line2', '')
                        order.shipping_city = address.get('city', '')
                        order.shipping_state = address.get('state', '')
                        order.shipping_postal_code = address.get('postal_code', '')
                        order.shipping_country = address.get('country', '')

                    order.save()

                    
                    if customer_email:
                        send_order_email(order)

                except Order.DoesNotExist:
                    pass
                    
    return HttpResponse(status=200)


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        cart[str(product_id)] += 1
    else:
        cart[str(product_id)] = 1

    request.session['cart'] = cart

    return redirect('cart_detail')

def cart_detail(request):
    cart = request.session.get('cart', {})

    cart_items = []
    total = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        subtotal = product.price * quantity
        total += subtotal
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })

    context = {
        'cart_items': cart_items,
        'total': total,
    }

    return render(request, 'cart_detail.html', context)


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})

   
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart  

    return redirect('cart_detail')

@csrf_exempt
def checkout(request):
    cart = request.session.get('cart', {})

    if not cart:
        return redirect('cart_detail')

    line_items = []
    order_ids = []

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        unit_amount = int(product.price * 100)

        # создаём заказ со статусом "pending"
        order = Order.objects.create(
            product=product,
            quantity=quantity,
            status="pending"
        )
        order_ids.append(str(order.id))

        # добавляем в Stripe line_items
        line_items.append({
            "price_data": {
                "currency": "eur",
                "product_data": {"name": product.name},
                "unit_amount": unit_amount,
            },
            "quantity": quantity,
        })

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url=settings.DOMAIN + reverse("stripe_success") + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=settings.DOMAIN + reverse("stripe_cancel"),
            metadata={"order_ids": ",".join(order_ids)},
            shipping_address_collection={
                "allowed_countries": [
                    "AT","BE","BG","HR","CY","CZ","DK","EE","FI","FR","DE","GR","HU","IE","IT",
                    "LV","LT","LU","MT","NL","PL","PT","RO","SK","SI","ES","SE","UA",
                ],
            },
        )

        # чистим корзину только после успешного создания сессии
        request.session['cart'] = {}

        return redirect(checkout_session.url)

    except Exception as e:
        return JsonResponse({"error": str(e)})


from django.contrib import admin
from django.urls import path
from apps.users import views
from apps.users.views import main,ProductListAPIView,ShopPageView,ConvertPriceView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main, name='main'),
    path('shop/', ShopPageView.as_view(), name='shop'),
    path('shop/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('api/products/', ProductListAPIView.as_view(), name='product_list'),
    path('convert-price/', ConvertPriceView.as_view(), name='convert_price'),
    path('create-checkout-session/<int:product_id>/', views.create_checkout_session, name='create_checkout_session'),
    path('stripe/webhook/', views.stripe_webhook, name='stripe-webhook'),
    path('success/', views.stripe_success, name='stripe_success'),  
    path('cancel/', views.stripe_cancel, name='stripe_cancel'), 
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path("cart/remove/<int:product_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("checkout/", views.checkout, name="checkout"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
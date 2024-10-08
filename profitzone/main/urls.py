from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('logout', auth_views.LogoutView.as_view(), name='logout'),
    path('catalogue/', views.catalogue, name='catalogue'),
    path('swedish_walls', views.swedish_walls, name='swedish_walls'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('horizontal_bars/', views.horizontal_bars, name='horizontal_bars'),
    path('swedish_walls/', views.swedish_walls, name='swedish_walls'),
    path('nutrition/', views.nutrition, name='nutrition'),
    path('lifting/', views.lifting, name='lifting'),
    path('racks/', views.racks, name='racks'),
    path('fitness/', views.fitness, name='fitness'),
    path('product_card/<int:id>/', views.product_card, name='product_card'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('cart', views.cart, name='cart'),
    path('update-quantity/', views.update_quantity, name='update_quantity'),
    path('remove-item/', views.remove_item, name='remove_item'),
    path('order', views.order, name='order'),
    path('delivery', views.delivery, name='delivery'),
    path('martial_arts/', views.martial_arts, name='martial_arts'),
    path('about', views.about, name='about'),
    path('contacts', views.contacts, name='contacts')




]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
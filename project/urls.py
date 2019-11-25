"""Swapit URL Configuration """

from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static

from Swapit import settings
from swapit_app import views

urlpatterns = [
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/home/'}, name='logout'),
    url(r'^admin/', admin.site.urls),
    url(r'^signup/', views.signup),
    url(r'^home/', views.index),

    url(r'^wishlist_add/', views.wishlist_add),
    url(r'^wishlist_remove/', views.wishlist_remove),
    url(r'^wishlist_get/', views.wishlist_get),

    url(r'^product/', views.product),
    url(r'^buy/', views.shop),
    url(r'^exchange/', views.exchange),
    url(r'^sell/', views.sell),
    url(r'^save_seller/', views.save_seller),

    url(r'^cart/', views.get_cart),
    url(r'^add_to_cart/', views.add_to_cart),
    url(r'^remove_from_cart/', views.remove_from_cart),
    url(r'^place_order/', views.place_order),
    url(r'^order_details/', views.order_details),
    url(r'^checkout/', views.checkout),
    url(r'^filter/', views.filter),
    url(r'^thankyou/', views.thankyou),

    url(r'^blog/', views.blog),
    url(r'^article/', views.article),
    url(r'^about/', views.about),
    url(r'^contact/', views.contact),
    url(r'^thankyou/', views.thankyou),
    url(r'^account_details/', views.account_details),
    url(r'^account_wishlist/', views.account_wishlist),
    url(r'^account_history/', views.account_history),
    url(r'^privacy_policy/', views.privacy_policy),
    url(r'^test/', views.test),
    url(r'^apply-promo-code/', views.apply_promo_code),
    url(r'^.txt', views.sslVerify),
    url(r'^login-with-facebook/', views.SignUpWithFaceBook),
    url(r'^$', views.index),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)\
  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

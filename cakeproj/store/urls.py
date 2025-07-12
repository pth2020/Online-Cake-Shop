from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    #Leave as empty string for a base url
    path('', views.home, name='home'),
    path('cake_categories/',views.cake_categories, name='cake_categories'),
    path('birthday_cakes/',views.birthday_cakes, name='birthday_cakes'),
    path('wedding_cakes/',views.wedding_cakes, name='wedding_cakes'),
    path('cupcakes/',views.cupcakes, name='cupcakes'),
    path('party_decorating/',views.party_decorating, name='party_decorating'),
    path('store/', views.store, name='store'),
    path('build_your_cake/', views.build_your_cake, name='build_your_cake'),
    path('wedding_cake_enquiry/', views.wedding_cake_enquiry, name='wedding_cake_enquiry'),
    path('wedding_cake_booking/', views.wedding_cake_booking, name='wedding_cake_booking'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('update_item/', views.update_item, name='update_item'),
    path('process_order/', views.process_order, name='process_order'),
    path('signin/', views.signin, name='signin'),
    path('signup/', views.signup, name='signup'),
    path('signout/', views.signout, name='signout'),
    path('testimonials/', views.testimonials, name='testimonials'),
    path('contact/', views.contact_view, name='contact'),
    path('thank_you/', views.thank_you, name='thank_you'),
    path('cake_description/<int:pk>/', views.cake_description, name='cake_description'),
    path('gallery/', views.gallery, name='gallery'),
    path('search/', views.search_view, name='search'),
    #Admin report
    path('secure-admin-area/',views.secure_admin_area, name='secure-admin-area'),
    path('update_transaction_view/', views.update_transaction_view, name='update_transaction_view'),
    # Password reset URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    # error page
    path('error/', views.error_page, name='error_page'),
    
]
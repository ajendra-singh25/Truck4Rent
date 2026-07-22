from django.urls import path
from . import views

urlpatterns = [

    # Home
    path('', views.index, name='home'),

    # Pages
    path('about', views.about, name='about'),
    path('services', views.services, name='services'),
    path('contact', views.contact, name='contact'),

    # Truck Owner Registration
    path(
        'owner-register/',
        views.owner_register,
        name='owner_register'
    ),

    # Customer Booking
    path(
        'create-booking/',
        views.create_booking,
        name='create_booking'
    ),

    # Booking Status
    path(
        'booking-status/<int:booking_id>/',
        views.booking_status,
        name='booking_status'
    ),
    path(
        'book-truck/',views.book_truck,name='book_truck'
        ),

    # Owner Actions
    path(
        'accept-booking/<int:booking_id>/',
        views.accept_booking,
        name='accept_booking'
    ),

    path(
        'reject-booking/<int:booking_id>/',
        views.reject_booking,
        name='reject_booking'
    ),
    path(
        'booking-status/<int:booking_id>/',
        views.booking_status,
        name='booking_status'
    ),
    path(
    "booking-status-api/<int:booking_id>/",
    views.booking_status_api,
    name="booking_status_api"
    ),
    path(
    "check-status/<int:booking_id>/",
    views.check_booking_status,
    name="check_booking_status",
),

]
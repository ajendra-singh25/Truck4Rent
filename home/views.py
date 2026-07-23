
from django.conf import settings
import requests
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import TruckOwner, Booking
from django.http import JsonResponse
from twilio.rest import Client
from django.shortcuts import render
from django.core.mail import EmailMultiAlternatives, get_connection
from django.conf import settings
from django.urls import reverse




# Home Page
def index(request):
    return render(request, 'index.html')


# Home Booking Form
def home(request):

    if request.method == "POST":

        customer_name = request.POST.get("customer_name")
        customer_mobile = request.POST.get("customer_mobile")

        pickup = request.POST.get("pickup_location")
        drop = request.POST.get("drop_location")

        owner = TruckOwner.objects.filter(
            available=True
        ).first()

        if owner:

            booking = Booking.objects.create(
                customer_name=customer_name,
                customer_mobile=customer_mobile,
                loading_location=pickup,
                unloading_location=drop,
                estimated_price=5000,
                truck_owner=owner,
                status="Pending"
            )

            return render(
                request,
                "booking_success.html",
                {
                    "booking": booking
                }
            )

        else:

            return render(
                request,
                "booking_failed.html"
            )

    return render(request, "index.html")


# About Page
def about(request):
    return render(request, 'about.html')


# Services Page
def services(request):
    return render(request, 'services.html')


# Contact Page
def contact(request):
    return render(request,"contact.html")


# Truck Owner Registration
def owner_register(request):

    if request.method == 'POST':

        TruckOwner.objects.create(
            owner_name=request.POST.get('owner_name'),
            mobile=request.POST.get('mobile'),
            email=request.POST.get('email'),
            city=request.POST.get('city'),
            truck_type=request.POST.get('truck_type'),
            truck_number=request.POST.get('truck_number')
        )

        return render(
            request,
            'owner_register.html',
            {
                'success': True
            }
        )

    return render(
        request,
        'owner_register.html'
    )
def send_owner_sms(owner, pickup, drop, price):

    url = "https://www.fast2sms.com/dev/bulkV2"

    payload = {
    "authorization": settings.FAST2SMS_API_KEY,
    "route": "q",
    "message": f"New Booking! Pickup:{pickup} Drop:{drop} Price: ₹{price}",
    "language": "english",
    "flash": 0,
    "numbers": owner.mobile
}

    try:
        response = requests.get(
            url,
            params=payload
        )

        print("SMS STATUS:", response.status_code)
        print("SMS RESPONSE:", response.text)

    except Exception as e:
        print("SMS Error:", e)
def send_owner_email(owner, booking, distance):

    BASE_URL = "https://truck4rent.onrender.com"

    accept_url = BASE_URL + reverse(
        "accept_booking",
        args=[booking.id]
    )

    reject_url = BASE_URL + reverse(
        "reject_booking",
        args=[booking.id]
    )

    subject = "🚚 New Truck Booking - Truck4Rent"

    html_message = f"""
    <html>

    <body style="font-family:Arial;background:#f4f4f4;padding:20px;">

    <div style="
        max-width:700px;
        margin:auto;
        background:white;
        border-radius:10px;
        padding:30px;
    ">

    <h2 style="color:#0d2b4d;">
    🚚 New Truck Booking
    </h2>

    <hr>

    <p><b>Customer:</b> {booking.customer_name}</p>

    <p><b>Mobile:</b> {booking.customer_mobile}</p>

    <p><b>Pickup:</b> {booking.loading_location}</p>

    <p><b>Drop:</b> {booking.unloading_location}</p>

    <p><b>Date:</b> {booking.booking_date}</p>

    <p><b>Distance:</b> {distance:.2f} KM</p>

    <h2 style="color:green;">
        ₹ {booking.estimated_price}
    </h2>

    <br>

    <a href="{accept_url}"
    style="
    background:#16a34a;
    color:white;
    padding:15px 30px;
    text-decoration:none;
    border-radius:8px;
    font-size:18px;
    ">
    ✅ Accept Booking
    </a>

    <br><br>

    <a href="{reject_url}"
    style="
    background:#dc2626;
    color:white;
    padding:15px 30px;
    text-decoration:none;
    border-radius:8px;
    font-size:18px;
    ">
    ❌ Reject Booking
    </a>

    <br><br>

    </div>

    </body>

    </html>
    """

    connection = get_connection(timeout=10)

    email = EmailMultiAlternatives(
        subject=subject,
        body="Truck Booking",
        from_email=settings.EMAIL_HOST_USER,
        to=[owner.email],
        connection=connection
    )

    email.attach_alternative(html_message, "text/html")

    try:
        email.send()

        print("Email Sent Successfully")

    except Exception as e:

        print("Email Error:", e)

# Create Booking
def create_booking(request):

    if request.method != "POST":
        return redirect("/")

    # Customer Details
    name = request.POST.get("customer_name")
    mobile = request.POST.get("customer_mobile")
    pickup = request.POST.get("pickup_location")
    drop = request.POST.get("drop_location")
    booking_date = request.POST.get("booking_date")

    # Find Available Truck Owner
    owner = TruckOwner.objects.filter(
        available=True
    ).first()

    if owner is None:

        return render(
            request,
            "booking_failed.html",
            {
                "message": "Sorry! No truck owner is available."
            }
        )

    # Default Values
    distance_km = 0
    price = 0

    try:

        pickup_lat = float(request.POST.get("pickup_lat"))
        pickup_lon = float(request.POST.get("pickup_lon"))

        drop_lat = float(request.POST.get("drop_lat"))
        drop_lon = float(request.POST.get("drop_lon"))

        url = (
            f"https://router.project-osrm.org/route/v1/driving/"
            f"{pickup_lon},{pickup_lat};"
            f"{drop_lon},{drop_lat}"
            f"?overview=false"
        )

        response = requests.get(
            url,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        if data.get("routes"):

            distance_km = (
                data["routes"][0]["distance"] / 1000
            )

            price = round(
                float(owner.rate_per_km) * distance_km,
                2
            )

    except Exception as e:

        print("Distance Error:", e)

    # Save Booking
    booking = Booking.objects.create(

        customer_name=name,

        customer_mobile=mobile,

        loading_location=pickup,

        unloading_location=drop,

        booking_date=booking_date,

        estimated_price=price,

        truck_owner=owner,

        status="Pending"
    )

    # Send Email (Don't stop booking if email fails)
    try:

        send_owner_email(
            owner,
            booking,
            distance_km
        )

    except Exception as e:

        print("Email Error:", e)

    # Go to Booking Status Page
    return redirect(
        "booking_status",
        booking.id
    )
def booking_status_api(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    return JsonResponse({
        "status":booking.status
    })



# Owner Accept Booking
def accept_booking(request, booking_id):

    try:

        booking = Booking.objects.get(id=booking_id)

    except Booking.DoesNotExist:

        return HttpResponse(
            "Booking not found.",
            status=404
        )

    booking.status = "Accepted"

    booking.save()

    if booking.truck_owner:

        booking.truck_owner.available = False

        booking.truck_owner.save()

    return render(
        request,
        "owner_response.html",
        {
            "message": "✅ Booking Accepted Successfully",
            "booking": booking
        }
    )
# Owner Reject Booking
def reject_booking(request, booking_id):

    try:

        booking = Booking.objects.get(id=booking_id)

    except Booking.DoesNotExist:

        return HttpResponse(
            "Booking not found.",
            status=404
        )

    booking.status = "Rejected"

    booking.save()

    if booking.truck_owner:

        booking.truck_owner.available = True

        booking.truck_owner.save()

    return render(
        request,
        "owner_response.html",
        {
            "message": "❌ Booking Rejected Successfully",
            "booking": booking
        }
    )

# Booking Status
def booking_status(request, booking_id):

    booking = Booking.objects.get(
        id=booking_id
    )

    return render(
        request,
        "booking_status.html",
        {
            "booking": booking
        }
    )
def book_truck(request):

    if request.method == "POST":

        pickup = request.POST.get("pickup")
        drop = request.POST.get("drop")

        owner = TruckOwner.objects.filter(
            available=True
        ).first()

        if not owner:

            return JsonResponse({
                "status": "failed",
                "message": "No truck available"
            })

        booking = Booking.objects.create(

            customer_name="Customer",

            customer_mobile="9999999999",

            loading_location=pickup,

            unloading_location=drop,

            estimated_price=5000,

            truck_owner=owner,

            status="Pending"
        )

        return JsonResponse({

            "status": "success",

            "booking_id": booking.id,

            "owner_name": owner.owner_name,

            "owner_mobile": owner.mobile,

            "price": 5000
        })

    return JsonResponse({
        "status": "error"
    })
def booking_accepted(request, booking_id):

    booking = Booking.objects.get(id=booking_id)

    return render(
        request,
        "booking_accepted.html",
        {
            "booking": booking
        }
    )
def booking_rejected(request, booking_id):

    booking = Booking.objects.get(id=booking_id)

    return render(
        request,
        "booking_rejected.html",
        {
            "booking": booking
        }
    )
def check_booking_status(request, booking_id):

    try:
        booking = Booking.objects.get(id=booking_id)

    except Booking.DoesNotExist:

        return JsonResponse(
            {
                "status": "Not Found"
            },
            status=404
        )

    return JsonResponse(
        {
            "status": booking.status,
            "price": str(booking.estimated_price),
            "owner": booking.truck_owner.owner_name if booking.truck_owner else "",
            "mobile": booking.truck_owner.mobile if booking.truck_owner else ""
        }
    )
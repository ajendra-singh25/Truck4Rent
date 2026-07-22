
from django.conf import settings
import requests
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import TruckOwner, Booking
from django.http import JsonResponse
from twilio.rest import Client
from django.shortcuts import render
from django.core.mail import EmailMultiAlternatives
from django.conf import settings




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

    BASE_URL = "https://nerd-shelter-laundry.ngrok-free.dev"

    accept_url = f"{BASE_URL}/accept-booking/{booking.id}/"
    reject_url = f"{BASE_URL}/reject-booking/{booking.id}/"

    subject = "🚚 New Truck Booking - Truck4Rent"

    html_message = f"""
    <!DOCTYPE html>
    <html>

    <body style="margin:0;padding:20px;background:#f4f6f9;font-family:Arial,sans-serif;">

    <table align="center"
           cellpadding="0"
           cellspacing="0"
           width="650"
           style="background:#ffffff;
                  border-radius:12px;
                  overflow:hidden;
                  box-shadow:0 5px 20px rgba(0,0,0,.15);">

        <!-- Header -->
        <tr>
            <td style="background:#0d2b4d;
                       color:white;
                       text-align:center;
                       padding:25px;">

                <h1 style="margin:0;">
                    🚚 Truck4Rent
                </h1>

                <p style="margin-top:10px;font-size:17px;">
                    New Truck Booking Request
                </p>

            </td>
        </tr>

        <!-- Booking Details -->
        <tr>

            <td style="padding:30px;">

                <h2 style="color:#0d2b4d;">
                    Booking Details
                </h2>

                <table width="100%" cellpadding="8">

                    <tr>
                        <td><b>Customer</b></td>
                        <td>{booking.customer_name}</td>
                    </tr>

                    <tr>
                        <td><b>Mobile</b></td>
                        <td>{booking.customer_mobile}</td>
                    </tr>

                    <tr>
                        <td><b>Pickup</b></td>
                        <td>{booking.loading_location}</td>
                    </tr>

                    <tr>
                        <td><b>Drop</b></td>
                        <td>{booking.unloading_location}</td>
                    </tr>

                    <tr>
                        <td><b>Booking Date</b></td>
                        <td>{booking.booking_date}</td>
                    </tr>

                    <tr>
                        <td><b>Distance</b></td>
                        <td>{distance:.2f} KM</td>
                    </tr>

                    <tr>
                        <td><b>Estimated Price</b></td>

                        <td style="
                            color:#16a34a;
                            font-size:22px;
                            font-weight:bold;">

                            ₹{booking.estimated_price}

                        </td>
                    </tr>

                </table>

                <br><br>

                <div style="text-align:center;">

                    <p>

                        <a href="{accept_url}"
                           style="
                           background:#16a34a;
                           color:white;
                           text-decoration:none;
                           padding:15px 28px;
                           border-radius:8px;
                           display:inline-block;
                           font-size:18px;
                           font-weight:bold;">

                           ✅ Accept Booking

                        </a>

                    </p>

                    <p>

                        <a href="{reject_url}"
                           style="
                           background:#dc2626;
                           color:white;
                           text-decoration:none;
                           padding:15px 28px;
                           border-radius:8px;
                           display:inline-block;
                           font-size:18px;
                           font-weight:bold;">

                           ❌ Reject Booking

                        </a>

                    </p>

                </div>

            </td>

        </tr>

        <!-- Footer -->

        <tr>

            <td style="
                background:#f5f5f5;
                text-align:center;
                padding:20px;
                color:#666;
                font-size:14px;">

                Thank you for being a Truck4Rent Partner.<br>
                Please respond to this booking as soon as possible.

            </td>

        </tr>

    </table>

    </body>
    </html>
    """

    email = EmailMultiAlternatives(
        subject=subject,
        body="You have received a new truck booking.",
        from_email=settings.EMAIL_HOST_USER,
        to=[owner.email],
    )

    email.attach_alternative(html_message, "text/html")
    email.send()

    print("✅ EMAIL SENT SUCCESSFULLY")

# Create Booking
def create_booking(request):

    if request.method == "POST":

        pickup = request.POST.get("pickup_location")
        drop = request.POST.get("drop_location")
        customer_email = request.POST.get("customer_email")

        name = request.POST.get("customer_name")
        mobile = request.POST.get("customer_mobile")
        booking_date = request.POST.get("booking_date")

        owner = TruckOwner.objects.filter(
            available=True
        ).first()

        if owner:

            try:

                pickup_lat = float(
                    request.POST.get("pickup_lat")
                )

                pickup_lon = float(
                    request.POST.get("pickup_lon")
                )

                drop_lat = float(
                    request.POST.get("drop_lat")
                )

                drop_lon = float(
                    request.POST.get("drop_lon")
                )

                url = (
                f"https://router.project-osrm.org/route/v1/driving/"
                f"{pickup_lon},{pickup_lat};{drop_lon},{drop_lat}"
                f"?overview=false"
                )

                response = requests.get(url)

                print("STATUS:", response.status_code)
                print("RESPONSE:", response.text)

                data = response.json()

                distance_km = (
                data["routes"][0]["distance"]
                / 1000
                )

                price = round(
                    float(owner.rate_per_km)
                    * distance_km,
                    2
                )

            except Exception as e:

                print("ERROR:",e)

                distance_km = 0
                price = 0
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
            print(settings.FAST2SMS_API_KEY)

            send_owner_email(
                owner,
                booking,
                distance_km,
    
             )
        return redirect("booking_status", booking.id)
   

                
            

        return render(
            request,
            "booking_failed.html"
        )

    return redirect("/")
def booking_status_api(request, booking_id):
    booking = Booking.objects.get(id=booking_id)
    return JsonResponse({
        "status":booking.status
    })



# Owner Accept Booking
def accept_booking(request, booking_id):

    booking = Booking.objects.get(id=booking_id)

    booking.status = "Accepted"
    booking.save()


    return render(
        request,
        "owner_response.html",
        {
            "message": "✅ Booking Accepted Successfully"
        }
    )
# Owner Reject Booking
def reject_booking(request, booking_id):

    booking = Booking.objects.get(id=booking_id)

    booking.status = "Rejected"
    booking.save()

    return render(
        request,
        "owner_response.html",
        {
            "message": "❌ Booking Rejected Successfully"
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

    booking = Booking.objects.get(id=booking_id)

    return JsonResponse({
        "status": booking.status
    })
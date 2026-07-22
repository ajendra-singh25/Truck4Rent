from django.db import models


# ============================
# Truck Owner Registration
# ============================

class TruckOwner(models.Model):

    owner_name = models.CharField(max_length=100)

    mobile = models.CharField(max_length=15)

    email = models.EmailField()

    city = models.CharField(max_length=100)

    truck_type = models.CharField(max_length=50)

    truck_number = models.CharField(max_length=30)

    available = models.BooleanField(default=True)

    rate_per_km = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=25.00
    )

    def __str__(self):
        return self.owner_name


# ============================
# Customer Booking
# ============================

class Booking(models.Model):

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    )

    customer_name = models.CharField(max_length=100)

    customer_mobile = models.CharField(
        max_length=15
    )

    loading_location = models.CharField(
        max_length=255
    )

    unloading_location = models.CharField(
        max_length=255
    )

    booking_date = models.DateField()

    estimated_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    truck_owner = models.ForeignKey(
        TruckOwner,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    arrival_time = models.TimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.loading_location} → {self.unloading_location}"
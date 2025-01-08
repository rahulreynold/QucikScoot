import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


# Simplified Custom User model
# models.py
class User(AbstractUser):
    email = models.EmailField(unique=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    user_role = models.CharField(max_length=50, choices=[('owner', 'Owner'), ('renter', 'Renter')])

    # Adding USER_ROLE_CHOICES as a class attribute
    USER_ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('renter', 'Renter'),
    ]

    def __str__(self):
        return self.username



# UserProfile model for storing additional user information
class UserProfile(models.Model):
    bio = models.CharField(max_length=200, null=True)
    profile_picture = models.ImageField(upload_to="profilepictures", null=True, blank=True, default="profilepictures/default.png")
    phone = models.CharField(max_length=200)
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    def __str__(self):
        return self.owner.username


# Category model for two-wheelers (e.g., Bike, Scooter)
class Category(models.Model):
    category_type = models.CharField(max_length=100)

    def __str__(self):
        return self.category_type


# TwoWheeler model for storing vehicle details
class TwoWheeler(models.Model):
    VEHICLE_TYPES = [
        ('petrol', 'Petrol'),
        ('electric', 'Electric'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    number_plate = models.CharField(max_length=20, unique=True)  # Unique vehicle number plate
    picture = models.ImageField(upload_to='two_wheeler_pics/')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='two_wheelers')
    price = models.FloatField()  # Rental price per day
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    vehicle_type = models.CharField(max_length=50, choices=VEHICLE_TYPES)
    mileage_or_range = models.FloatField()  # Mileage (km/l) for petrol or range (km) for electric vehicles

    def __str__(self):
        return self.title


class Booking(models.Model):
    renter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    two_wheeler = models.ForeignKey(TwoWheeler, on_delete=models.CASCADE, related_name='bookings')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    total_price = models.FloatField()
    status = models.CharField(
        max_length=50,
        choices=[("pending", "Pending"), ("confirmed", "Confirmed"), ("completed", "Completed")],
        default="pending"
    )
    order_id = models.CharField(max_length=100, unique=True, blank=True, null=True)  # Unique order ID
    is_order_placed = models.BooleanField(default=False)  # Add this field

    def save(self, *args, **kwargs):
        if not self.order_id:  # Generate order ID if it doesn't already exist
            self.order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking by {self.renter.username} - Order ID: {self.order_id}"



# Payment model for handling payments associated with bookings
class Payment(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    payment_type = models.CharField(max_length=50, choices=[("upi", "UPI"), ("card", "Card"), ("paypal", "PayPal")])
    is_paid = models.BooleanField(default=False)
    payment_date = models.DateTimeField(null=True, blank=True)
    amount = models.FloatField()
    payment_status = models.CharField(max_length=50, choices=[("pending", "Pending"), ("failed", "Failed"), ("completed", "Completed")])

    def __str__(self):
        return f"Payment for Booking {self.booking.id}"


# Review model for allowing renters to leave feedback
class Review(models.Model):
    two_wheeler = models.ForeignKey(TwoWheeler, on_delete=models.CASCADE, related_name='reviews')
    renter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])
    review_message = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.renter.username} for {self.two_wheeler.title}"


# Notification model for sending alerts and updates to users
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:50]}"


# Checkout model for finalizing the booking and payment process
class Checkout(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE)
    is_checked_out = models.BooleanField(default=False)

    def __str__(self):
        return f"Checkout for {self.booking.renter.username} - {self.booking.two_wheeler.title}"


# Analytics model for tracking platform performance
class Analytics(models.Model):
    total_bookings = models.IntegerField()
    total_revenue = models.FloatField()
    active_users = models.IntegerField()
    date = models.DateTimeField()

    def __str__(self):
        return f"Analytics for {self.date.date()}"

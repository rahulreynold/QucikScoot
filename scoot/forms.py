from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, UserProfile, TwoWheeler, Category, Booking, Review, Payment
from django.forms import DateInput
from datetime import datetime
from django.utils import timezone

# SignUpForm for new user registration
# class SignUpForm(UserCreationForm):
#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password1', 'password2', 'user_role']
#         widgets = {
#             'user_role': forms.Select(choices=User.USER_ROLE_CHOICES),
#         }


from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'user_role']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',  # Apply Bootstrap form-control class
                'placeholder': 'Enter your username',  # Add placeholder text
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',  # Bootstrap styling for email field
                'placeholder': 'Enter your email',  # Add placeholder
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'form-control',  # Bootstrap styling for password field
                'placeholder': 'Enter your password',  # Add placeholder
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-control',  # Bootstrap styling for password confirmation
                'placeholder': 'Confirm your password',  # Add placeholder
            }),
            'user_role': forms.Select(choices=User.USER_ROLE_CHOICES, attrs={
                'class': 'form-select',  # Bootstrap class for select input
                'placeholder': 'Choose your role',  # Add placeholder
            }),
        }

# Login form for user authentication
# class LoginForm(AuthenticationForm):
#     class Meta:
#         model = User
#         fields = ['username', 'password']

class SignInForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

# User Profile update form
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_picture', 'phone']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'cols': 30}),
        }

        
class TwoWheelerForm(forms.ModelForm):
    class Meta:
        model = TwoWheeler
        fields = ['title', 'description', 'number_plate', 'picture', 'price', 'category', 'vehicle_type', 'mileage_or_range']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    # Ensure category field uses ModelChoiceField to display the options from Category model
    category = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label="Select Category")


# forms.py
class BookingDateForm(forms.Form):
    start_date = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    end_date = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        # If both dates are valid, we proceed with validation
        if start_date and end_date:
            # Convert to naive datetime (removes any timezone awareness)
            start_date = start_date.replace(tzinfo=None)
            end_date = end_date.replace(tzinfo=None)

            # Check if start_date is later than end_date
            if start_date >= end_date:
                raise forms.ValidationError("Start date must be before end date.")

            # Check if start_date is in the past
            if start_date < datetime.now():
                raise forms.ValidationError("Start date cannot be in the past.")

        cleaned_data['start_date'] = start_date
        cleaned_data['end_date'] = end_date

        return cleaned_data



# TwoWheeler form for adding/editing vehicles
# class TwoWheelerForm(forms.ModelForm):
#     class Meta:
#         model = TwoWheeler
#         fields = ['title', 'description', 'number_plate', 'picture', 'price', 'category', 'vehicle_type', 'mileage_or_range']
#         widgets = {
#             'description': forms.Textarea(attrs={'rows': 3}),
#         }

# # Booking form to track the rental process
# class BookingForm(forms.ModelForm):
#     class Meta:
#         model = Booking
#         fields = ['two_wheeler', 'start_date', 'end_date']
#         widgets = {
#             'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
#             'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
#         }

# # Review form for renters to leave feedback on two-wheelers
# class ReviewForm(forms.ModelForm):
#     class Meta:
#         model = Review
#         fields = ['rating', 'review_message']
#         widgets = {
#             'review_message': forms.Textarea(attrs={'rows': 3}),
#         }

# # Payment form for payment processing
# class PaymentForm(forms.ModelForm):
#     class Meta:
#         model = Payment
#         fields = ['payment_type', 'amount']
#         widgets = {
#             'payment_type': forms.Select(choices=Payment.PAYMENT_TYPE_CHOICES),
#         }

# # Checkout form to finalize booking and payment
# class CheckoutForm(forms.ModelForm):
#     class Meta:
#         model = Booking
#         fields = ['total_price', 'status']
#         widgets = {
#             'status': forms.Select(choices=Booking.STATUS_CHOICES),
        # }


from django import forms
from django.forms import DateInput
from .models import Booking
from datetime import datetime

class BookingForm(forms.ModelForm):
    start_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local',  # Makes use of the HTML5 datetime-local input type
        }),
        required=True
    )
    
    end_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local',  # Makes use of the HTML5 datetime-local input type
        }),
        required=True
    )

    class Meta:
        model = Booking
        fields = ['start_date', 'end_date']
        
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        # Ensure start date is before end date
        if start_date and end_date:
            if start_date >= end_date:
                raise forms.ValidationError("Start date must be before end date.")

            # Ensure start date is not in the past
            if start_date < datetime.now():
                raise forms.ValidationError("Start date cannot be in the past.")
        
        return cleaned_data

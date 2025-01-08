from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.generic import View, FormView, CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
# from django.db.models import Sum
# from django.core.mail import send_mail
# from django.utils.decorators import method_decorator
# from django.views.decorators.csrf import csrf_exempt
# from django.views.decorators.cache import never_cache
# from decouple import config
# from twilio.rest import Client
# from scoot.models import TwoWheeler, Review, UserProfile, Booking
from scoot.models import TwoWheeler,UserProfile,Booking
# from scoot.forms import SignUpForm, SignInForm, UserProfileForm, TwoWheelerForm, ReviewForm, PasswordResetForm
from scoot.forms import SignUpForm,TwoWheelerForm,UserProfileForm,BookingDateForm,SignInForm
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from datetime import datetime
from .forms import SignInForm
from django.http import HttpResponse


# View for the owner's dashboard
@login_required
def owner_dashboard_view(request):
    # Add any logic you need for the owner dashboard
    return render(request, 'owner_dashboard.html')

# View for the renter's dashboard
@login_required
def renter_dashboard_view(request):
    # Add any logic you need for the renter dashboard
    return render(request, 'renter_dashboard.html')



class SignUpView(CreateView):
    template_name = 'register.html'
    form_class = SignUpForm
    success_url = reverse_lazy("signin")


class SignInView(FormView):
    template_name = 'login.html'
    form_class = SignInForm

    def post(self, request, *args, **kwargs):

        form_instance = self.form_class(request.POST)
 
        if form_instance.is_valid():
            username = form_instance.cleaned_data.get("username")
            password = form_instance.cleaned_data.get("password")
            user = authenticate(username=username, password=password)

            if user:
                login(request, user) 
                if user.user_role == 'owner':
                    return redirect('owner_dashboard')
                elif user.user_role == 'renter':
                    return redirect('renter-dashboard')
                else:
                    messages.error(request, 'Invalid role.')
                    return redirect('signin')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            print("Form validation errors:", form_instance.errors)

        return render(request, self.template_name, {'form': form_instance})




class SignoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect("signin")
    

class UserProfileView(View):
    template_name = "profile_view.html"

    def get(self, request, *args, **kwargs):
        # Check if the user has a profile; if not, create one
        try:
            profile_instance = request.user.profile
        except UserProfile.DoesNotExist:
            # Create the profile if it doesn't exist
            profile_instance = UserProfile.objects.create(owner=request.user)
        
        return render(request, self.template_name, {"profile": profile_instance})



class UserProfileEditView(View):
    template_name = "profile_edit.html"
    form_class = UserProfileForm

    def get(self, request, *args, **kwargs):
        profile_instance = request.user.profile
        form_instance = self.form_class(instance=profile_instance)
        return render(request, self.template_name, {"form": form_instance})

    def post(self, request, *args, **kwargs):
        profile_instance = request.user.profile
        form_instance = self.form_class(request.POST, instance=profile_instance, files=request.FILES)
        if form_instance.is_valid():
            form_instance.save()
            return redirect("profile-view")
        return render(request, self.template_name, {"form": form_instance})
    

class AboutUsView(View):
    template_name = "aboutus.html"

    def get(self, request, *args, **kwargs):
  
        context = {
            "company_name": "QuickScoot",
            "mission_statement": "Providing fast, affordable, and convenient two-wheeler rentals for all.",
            "contact_email": "rahul@quickscoot.com",
            "contact_phone": "+8547231461",
        }
        return render(request, self.template_name, context)
    


class ContactUsView(View):
    template_name = "contactus.html"

    def get(self, request, *args, **kwargs):
        # Return the Contact Us page template when the GET request is made
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        # Handle the form submission
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        
        # Here, you can add logic to send an email or save the message to the database
        # For example:
        # send_email(name, email, message)
        
        # For now, just return a simple confirmation response
        # You can redirect to a "thank you" page or show a success message
        return HttpResponse("Thank you for contacting us. We will get back to you shortly!")
    

# class RenterProfileView(View):
#     template_name = "renter_profile_view.html"

#     def get(self, request, *args, **kwargs):
#         if request.user.user_role != 'renter':
#             return redirect("unauthorized")  # Redirect if the user is not a renter
        
#         # Get the user's profile
#         profile_instance = request.user.profile
#         return render(request, self.template_name, {"profile": profile_instance, "user": request.user})


class RenterProfileView(View):
    template_name = "renter_profile_view.html"

    def get(self, request, *args, **kwargs):
        # Check if the user has a profile; if not, create one
        try:
            profile_instance = request.user.profile
        except UserProfile.DoesNotExist:
            # Create the profile if it doesn't exist
            profile_instance = UserProfile.objects.create(owner=request.user)

        return render(request, self.template_name, {"profile": profile_instance})




class RenterProfileEditView(View):
    template_name = "renter_profile_edit.html"
    form_class = UserProfileForm

    def get(self, request, *args, **kwargs):
        # Ensure that the user is a renter
        if request.user.user_role != 'renter':
            return redirect("unauthorized")  # Redirect if the user is not a renter
        
        # Get the user's profile and initialize the form
        profile_instance = request.user.profile
        form_instance = self.form_class(instance=profile_instance)
        return render(request, self.template_name, {"form": form_instance})

    def post(self, request, *args, **kwargs):
        # Ensure that the user is a renter
        if request.user.user_role != 'renter':
            return redirect("unauthorized")  # Redirect if the user is not a renter
        
        profile_instance = request.user.profile
        form_instance = self.form_class(request.POST, instance=profile_instance, files=request.FILES)
        
        if form_instance.is_valid():
            form_instance.save()
            return redirect("renter-profile-view")
        
        return render(request, self.template_name, {"form": form_instance})




class TwoWheelerCreateView(View):
    template_name = "two_wheeler_add.html"
    form_class = TwoWheelerForm

    def get(self, request, *args, **kwargs):
        form_instance = self.form_class()
        return render(request, self.template_name, {"form": form_instance})

    def post(self, request, *args, **kwargs):
        form_instance = self.form_class(request.POST, files=request.FILES)
        form_instance.instance.owner = request.user
        if form_instance.is_valid():
            form_instance.save()
            return redirect("owner_dashboard")
        return render(request, self.template_name, {"form": form_instance})

class MyTwoWheelerListView(View):
    template_name = "owner-vehicles_list.html"

    def get(self, request, *args, **kwargs):
        vehicles = TwoWheeler.objects.filter(owner=request.user)
        for vehicle in vehicles:
            vehicle.discounted_price=vehicle.price+200
        return render(request, self.template_name, {"vehicles": vehicles})

class TwoWheelerEditView(View):
    template_name = "two_wheeler_edit.html"  # Create a corresponding HTML template
    form_class = TwoWheelerForm

    def get(self, request, *args, **kwargs):
        id = kwargs.get("pk")  # Get the primary key of the TwoWheeler to edit
        tw_object = get_object_or_404(TwoWheeler, id=id, owner=request.user)  # Ensure the current user owns this object
        form_instance = self.form_class(instance=tw_object)
        return render(request, self.template_name, {"form": form_instance})

    def post(self, request, *args, **kwargs):
        id = kwargs.get("pk")
        tw_object = get_object_or_404(TwoWheeler, id=id, owner=request.user)
        form_instance = self.form_class(request.POST, request.FILES, instance=tw_object)

        if form_instance.is_valid():
            form_instance.save()
            return redirect("two-wheeler-list")  # Redirect to the list or detail view after saving

        return render(request, self.template_name, {"form": form_instance})


class TwoWheelerDeleteView(View):
    template_name = "two_wheeler_delete.html"  # Create a confirmation template

    def get(self, request, *args, **kwargs):
        id = kwargs.get("pk")  # Get the primary key of the TwoWheeler to delete
        tw_object = get_object_or_404(TwoWheeler, id=id, owner=request.user)  # Ensure current user owns this object
        return render(request, self.template_name, {"object": tw_object})

    def post(self, request, *args, **kwargs):
        id = kwargs.get("pk")
        tw_object = get_object_or_404(TwoWheeler, id=id, owner=request.user)
        tw_object.delete()
        return redirect("two-wheeler-list")  # Redirect to the list view after deletion
    
class AvailableDateView(View):
    template_name = 'date_selection.html'

    def get(self, request, *args, **kwargs):
        form = BookingDateForm(request.GET or None)

        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']

            # Redirect to the list of vehicles or a specific vehicle
            # Example: Redirect to the first available vehicle
            vehicle_id = 1  # Replace with actual vehicle selection logic
            return redirect(f'/vehicle/{vehicle_id}/?start_date={start_date}&end_date={end_date}')

        return render(request, self.template_name, {'form': form})
    

from datetime import datetime

class VehicleListView(View):
    template_name = "vehicle_list.html"

    def get(self, request, *args, **kwargs):
        # Get start and end dates from the query parameters
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        # Check if both start and end date are provided
        if start_date_str and end_date_str:
            try:
                # Convert strings to datetime
                start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M')
                end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M')
                # Format the date to exclude time
                available_dates = f"Available from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
            except ValueError:
                start_date = None
                end_date = None
                available_dates = None
        else:
            start_date = None
            end_date = None
            available_dates = None

        # Get the vehicles
        vehicles = TwoWheeler.objects.all()  # Adjust your query as needed

        return render(
            request,
            self.template_name,
            {
                'vehicles': vehicles,
                'start_date': start_date,
                'end_date': end_date,
                'available_dates': available_dates,
            }
        )


from datetime import datetime
from django.shortcuts import get_object_or_404, render
from django.views import View
from .models import TwoWheeler

class SeeVehicleDetailView(View):
    template_name = "vehiclefull_detail.html"

    def get(self, request, *args, **kwargs):
        vehicle_id = kwargs.get("pk")
        vehicle = get_object_or_404(TwoWheeler, id=vehicle_id)
        owner = vehicle.owner

        # Get start and end date from query parameters
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        # Initialize variables
        start_date = None
        end_date = None
        total_price = 0

        if start_date_str and end_date_str:
            try:
                # Convert string to datetime
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

                # Calculate the number of days
                delta = end_date - start_date
                total_price = vehicle.price * delta.days
            except ValueError:
                start_date = None
                end_date = None
                total_price = 0

        return render(
            request, 
            self.template_name, 
            {
                'vehicle': vehicle,
                'owner': owner,
                'start_date': start_date,
                'end_date': end_date,
                'total_price': total_price,
            }
        )



    
class TotalPriceView(View):
    template_name = 'total_price.html'

    def get(self, request, *args, **kwargs):
        vehicle_id = kwargs.get('pk')  # Vehicle ID from URL
        vehicle = get_object_or_404(TwoWheeler, pk=vehicle_id)  # Fetch vehicle from database

        # Get dates from the query parameters
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        if start_date_str and end_date_str:
            try:
                # Convert string to datetime
                start_date = datetime.fromisoformat(start_date_str)
                end_date = datetime.fromisoformat(end_date_str)

                # Ensure valid date range
                if start_date >= end_date:
                    raise ValueError("Start date must be before end date.")
                if start_date < datetime.now():
                    raise ValueError("Start date cannot be in the past.")
            except ValueError as e:
                # Handle invalid date input
                return render(request, self.template_name, {
                    'vehicle': vehicle,
                    'error_message': str(e),
                })
        else:
            return render(request, self.template_name, {
                'vehicle': vehicle,
                'error_message': "Start and end dates are required.",
            })

        # Calculate booking duration and total price
        total_days = (end_date - start_date).days
        total_price = total_days * vehicle.price

        context = {
            'vehicle': vehicle,
            'start_date': start_date,
            'end_date': end_date,
            'total_days': total_days,
            'total_price': total_price,
        }
        return render(request, self.template_name, context)


# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.utils import timezone
# from .models import Booking, TwoWheeler
# from .forms import BookingForm

# class BookingView(View):
#     template_name = 'booking_confirmation.html'

#     def get(self, request, *args, **kwargs):
#         vehicle_id = kwargs.get('pk')
#         vehicle = get_object_or_404(TwoWheeler, id=vehicle_id)

#         # Display the form with the vehicle details and no total price yet
#         form = BookingForm()

#         return render(request, self.template_name, {
#             'vehicle': vehicle,
#             'form': form,
#         })

#     def post(self, request, *args, **kwargs):
#         vehicle_id = kwargs.get('pk')
#         vehicle = get_object_or_404(TwoWheeler, id=vehicle_id)

#         form = BookingForm(request.POST)
        
#         if form.is_valid():
#             start_date = form.cleaned_data['start_date']
#             end_date = form.cleaned_data['end_date']

#             # Calculate total price based on the vehicle price
#             delta = end_date - start_date
#             total_price = vehicle.price * delta.days

#             # Create and save the booking
#             booking = Booking(
#                 user=request.user,
#                 two_wheeler=vehicle,
#                 start_date=start_date,
#                 end_date=end_date,
#                 total_price=total_price
#             )
#             booking.save()

#             # Redirect to a confirmation page or display success message
#             messages.success(request, "Booking confirmed successfully!")
#             return redirect('booking_confirmation', pk=booking.id)

#         # If the form is not valid, return the same page with error messages
#         return render(request, self.template_name, {
#             'vehicle': vehicle,
#             'form': form,
#         })

from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib import messages
from datetime import datetime
from .models import TwoWheeler, Booking

class BookVehicleView(View):
    template_name = 'booking_confirmation.html'  # Adjust the template name as needed

    def get(self, request, *args, **kwargs):
        # Fetch vehicle details to display in the booking form
        vehicle_id = kwargs.get('pk')
        vehicle = get_object_or_404(TwoWheeler, id=vehicle_id)
        return render(request, self.template_name, {'vehicle': vehicle})

    def post(self, request, *args, **kwargs):
        vehicle_id = kwargs.get('pk')  # Vehicle ID from the URL
        vehicle = get_object_or_404(TwoWheeler, id=vehicle_id)

        # Get form data
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')

        # Validate start and end dates
        if not start_date_str or not end_date_str:
            messages.error(request, "Start date and end date are required.")
            return render(request, self.template_name, {'vehicle': vehicle})

        try:
            # Parse the dates
            start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M')  # Adjust format as needed
            end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M')

            # Ensure valid date range
            if start_date >= end_date:
                raise ValueError("Start date must be before end date.")
            if start_date < datetime.now():
                raise ValueError("Start date cannot be in the past.")

            # Calculate total price
            total_days = (end_date - start_date).days + 1  # Including the last day
            total_price = total_days * vehicle.price

            # Debugging prints
            print("Booking Inputs:")
            print("Renter:", request.user)
            print("TwoWheeler:", vehicle)
            print("Start Date:", start_date)
            print("End Date:", end_date)
            print("Total Price:", total_price)

            # Save the booking
            booking = Booking.objects.create(
                renter=request.user,  # Ensure the user is authenticated
                two_wheeler=vehicle,
                start_date=start_date,
                end_date=end_date,
                total_price=total_price,
                status="pending",  # Default status
                is_order_placed=False  # Default value
            )

            # Redirect or display a success message
            messages.success(request, "Booking confirmed successfully!")
            return redirect('booking_confirmation', pk=booking.id)

        except ValueError as e:
            messages.error(request, str(e))
            return render(request, self.template_name, {'vehicle': vehicle})

        

from django.shortcuts import render, get_object_or_404
from django.views import View
from .models import Booking


class BookingSuccessView(View):
    template_name = 'booking_success.html'

    def get(self, request, *args, **kwargs):
        booking_id = kwargs.get('pk')  # Booking ID from the URL
        booking = get_object_or_404(Booking, id=booking_id)

        # Print data to the terminal
        print("Booking ID:", booking.id)
        print("Vehicle Title:", booking.two_wheeler.title)
        print("Start Date:", booking.start_date)
        print("End Date:", booking.end_date)
        print("Total Price:", booking.total_price)
        print("Owner Name:", booking.two_wheeler.owner.username)
        print("Owner Email:", booking.two_wheeler.owner.email)

        return render(request, self.template_name, {'booking': booking})









# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib import messages
# from .models import Booking, TwoWheeler
# from django.utils import timezone
# import uuid

# class CheckoutView(View):
#     def get(self, request, *args, **kwargs):
#         pk = kwargs.get('pk')  # Get the vehicle PK from URL
#         vehicle = get_object_or_404(TwoWheeler, pk=pk)  # Get the vehicle object by pk

#         # Retrieve start and end dates from the request
#         start_date = request.GET.get('start_date')
#         end_date = request.GET.get('end_date')

#         # Process the dates and calculate the total price
#         total_price = self.calculate_total_price(vehicle.price, start_date, end_date)

#         context = {
#             'vehicle': vehicle,
#             'start_date': start_date,
#             'end_date': end_date,
#             'total_price': total_price
#         }

#         return render(request, 'checkout.html', context)

#     def post(self, request, *args, **kwargs):
#         pk = kwargs.get('pk')  # Get the vehicle PK from URL
#         vehicle = get_object_or_404(TwoWheeler, pk=pk)  # Get the vehicle object by pk
        
#         start_date = request.POST.get('start_date')
#         end_date = request.POST.get('end_date')
#         total_price = float(request.POST.get('total_price'))
        
#         # Create a booking instance
#         booking = Booking(
#             renter=request.user,  # Set the current user as the renter
#             two_wheeler=vehicle,  # Set the selected vehicle
#             start_date=start_date,  # Set the start date
#             end_date=end_date,  # Set the end date
#             total_price=total_price,  # Set the total price
#             status='pending',  # Default status
#             order_id=f"ORD-{uuid.uuid4().hex[:8].upper()}",  # Generate unique order ID
#             is_order_placed=True  # Mark the order as placed
#         )

#         # Save the booking instance to the database
#         booking.save()

#         # Display a success message
#         messages.success(request, f"Booking successful! Your order ID is {booking.order_id}")
        
#         return redirect('booking_confirmation', order_id=booking.order_id)

#     def calculate_total_price(self, price_per_day, start_date, end_date):
#         # Convert start and end date to datetime objects
#         start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d')
#         end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d')

#         # Calculate the number of days
#         num_days = (end_date - start_date).days

#         # Calculate total price
#         total_price = price_per_day * num_days
#         return total_price




# from django.shortcuts import render
# from django.views import View
# from .models import Booking, Payment

# class MyOrderView(View):
#     template_name = "my_order.html"

#     def get(self, request, *args, **kwargs):
#         # Fetch all bookings for the logged-in user
#         bookings = Booking.objects.filter(renter=request.user).order_by('-start_date')

#         # Pass the bookings to the template
#         return render(request, self.template_name, {"bookings": bookings})




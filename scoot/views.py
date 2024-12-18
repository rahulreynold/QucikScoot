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


#working one
# class SignInView(FormView):
#     template_name = 'login.html'
#     form_class = SignInForm

#     def post(self, request, *args, **kwargs):
#         form = self.form_class(request.POST)  # Instantiate the form with POST data
#         if form.is_valid():
#             username = form.cleaned_data.get("username")
#             password = form.cleaned_data.get("password")
#             user = authenticate(username=username, password=password)

#             if user:
#                 login(request, user)  # Log the user in
#                 # Redirect based on user role
#                 if hasattr(user, 'user_role'):  # Ensure user_role exists
#                     if user.user_role == 'owner':
#                         return redirect('owner_dashboard')
#                     elif user.user_role == 'renter':
#                         return redirect('renter-dashboard')
#                     else:
#                         messages.error(request, 'Invalid role. Contact support.')
#                 else:
#                     messages.error(request, 'User role is not defined.')
#             else:
#                 messages.error(request, 'Invalid username or password.')
#         else:
#             messages.error(request, 'Form validation failed. Please check your inputs.')

#         # Re-render the form with errors if validation fails or login fails
#         return render(request, self.template_name, {'form': form})



# class IndexView(TemplateView):
#     template_name = 'index.html'

#     def get(self, request, *args, **kwargs):
#         vehicles = TwoWheeler.objects.all().exclude(owner=request.user)
#         return render(request, self.template_name, {"vehicles": vehicles})

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
            return redirect("owner_dashboard")
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
    

# #workind 
# class VehicleListView(View):
#     template_name = "vehicle_list.html"

#     def get(self, request, *args, **kwargs):
#         # Fetch all vehicles available for rent
#         vehicles = TwoWheeler.objects.all()

#         # Pass the vehicles to the template
#         return render(request, self.template_name, {'vehicles': vehicles})

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

        # Extract start_date and end_date from the query parameters
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        start_date = None
        end_date = None
        total_price = 0

        # If both start_date and end_date are provided, process them
        if start_date_str and end_date_str:
            try:
                # Parse the date strings (ignoring the time part)
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')  # Only the date part
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')  # Only the date part

                # Ensure end_date is after start_date
                if end_date > start_date:
                    # Calculate the number of rental days
                    rental_days = (end_date - start_date).days
                    if rental_days > 0:
                        # Calculate the total price
                        total_price = rental_days * vehicle.price
                else:
                    start_date = None
                    end_date = None
            except ValueError:
                # If there's an issue with the date format, reset the dates
                start_date = None
                end_date = None

        # Format the start_date and end_date for display purposes
        formatted_start_date = start_date.strftime('%Y-%m-%d') if start_date else "Not selected"
        formatted_end_date = end_date.strftime('%Y-%m-%d') if end_date else "Not selected"

        # Pass the data to the template
        return render(
            request,
            self.template_name,
            {
                'vehicle': vehicle,
                'start_date': formatted_start_date,
                'end_date': formatted_end_date,
                'total_price': total_price,
            }
        )





# # this is working
# class SeeVehicleDetailView(View):
#     template_name = "vehiclefull_detail.html"

#     def get(self, request, *args, **kwargs):
#         vehicle_id = kwargs.get("pk")
#         vehicle = get_object_or_404(TwoWheeler, id=vehicle_id)
#         owner = vehicle.owner

#         context = {
#             "vehicle": vehicle,
#             "owner": {
#                 "username": owner.username,
#                 "email": owner.email,
#             },
#         }
#         return render(request, self.template_name, context)

    
from datetime import datetime

class SeeVehicleDetailView(View):
    template_name = "vehiclefull_detail.html"

    def get(self, request, *args, **kwargs):
        vehicle_id = kwargs.get("pk")
        vehicle = get_object_or_404(TwoWheeler, id=vehicle_id)
        owner = vehicle.owner

        # Get start and end date from query parameters
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        # Check if both start and end date are provided
        if start_date_str and end_date_str:
            try:
                # Convert string to datetime
                start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M')
                end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M')

                # Calculate the number of days
                delta = end_date - start_date
                total_price = vehicle.price * delta.days
            except ValueError:
                start_date = None
                end_date = None
                total_price = 0
        else:
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






# class SeeVehicleDetailView(View):
#     template_name = "vehiclefull_detail.html"

#     def get(self, request, *args, **kwargs):
#         vehicle_id = kwargs.get("pk")
#         vehicle = get_object_or_404(TwoWheeler, id=vehicle_id)
#         owner = vehicle.owner

#         # Get start_date and end_date from query parameters
#         start_date_str = request.GET.get("start_date")
#         end_date_str = request.GET.get("end_date")

#         # Validate dates
#         if not start_date_str or not end_date_str:
#             return render(request, "error.html", {"message": "Start and end dates are required."})

#         try:
#             start_date = datetime.fromisoformat(start_date_str)
#             end_date = datetime.fromisoformat(end_date_str)

#             # Ensure valid date range
#             if start_date >= end_date:
#                 raise ValueError("Start date must be before end date.")
#             if start_date < datetime.now():
#                 raise ValueError("Start date cannot be in the past.")
#         except ValueError as e:
#             return render(request, "error.html", {"message": str(e)})

#         # Calculate the total price
#         total_days = (end_date - start_date).days
#         total_price = total_days * vehicle.price

#         renter = None
#         if request.user.user_role == "renter":
#             renter = request.user  # If the logged-in user is a renter, display their details

#         context = {
#             "vehicle": vehicle,
#             "owner": owner,
#             "start_date": start_date,
#             "end_date": end_date,
#             "total_days": total_days,
#             "total_price": total_price,
#             "renter": renter,
#         }
#         return render(request, self.template_name, context)


    
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








# class TotalPriceView(View):
#     template_name = 'total_price.html'

#     def get(self, request, *args, **kwargs):
#         # Fetch booking using pk from the URL
#         booking = get_object_or_404(Booking, pk=kwargs.get('pk'))  # Use pk instead of booking_id

#         # Get vehicle details from the booking
#         vehicle = booking.two_wheeler
#         renter = booking.renter  # Renter of the vehicle
#         owner = vehicle.owner  # Owner of the vehicle

#         # Calculate the number of days of booking
#         booking_duration = booking.end_date - booking.start_date
#         total_days = booking_duration.days

#         # Calculate total price
#         total_price = total_days * vehicle.price

#         # Prepare context to pass to the template
#         context = {
#             'booking': booking,
#             'vehicle': vehicle,
#             'renter': renter,
#             'owner': owner,
#             'total_days': total_days,
#             'total_price': total_price,
#         }

#         return render(request, self.template_name, context)

# class TotalPriceView(View):
#     template_name = 'total_price.html'

#     def get(self, request, *args, **kwargs):
#         vehicle_id = kwargs.get('pk')  # Get vehicle ID from URL
#         vehicle = get_object_or_404(TwoWheeler, pk=vehicle_id)  # Get the vehicle object
#         start_date_str = request.GET.get('start_date')  # Get start date from URL
#         end_date_str = request.GET.get('end_date')  # Get end date from URL

#         if not start_date_str or not end_date_str:
#             return render(request, 'error.html', {'message': 'Start and end dates are required.'})

#         # Convert the string to datetime objects
#         start_date = datetime.fromisoformat(start_date_str)
#         end_date = datetime.fromisoformat(end_date_str)

#         # Calculate the number of days for the rental
#         booking_duration = end_date - start_date
#         total_days = booking_duration.days

#         # Calculate the total price
#         total_price = total_days * vehicle.price

#         context = {
#             'vehicle': vehicle,
#             'total_days': total_days,
#             'total_price': total_price,
#             'start_date': start_date,
#             'end_date': end_date,
#         }

#         return render(request, self.template_name, context)



# class AddReviewView(View):
#     template_name = "add_review.html"
#     form_class = ReviewForm

#     def post(self, request, *args, **kwargs):
#         form_instance = self.form_class(request.POST)
#         vehicle_id = kwargs.get("pk")
#         vehicle = get_object_or_404(TwoWheeler, id=vehicle_id)
#         if form_instance.is_valid():
#             review = form_instance.save(commit=False)
#             review.user = request.user
#             review.vehicle = vehicle
#             review.save()
#             return redirect("two-wheeler-detail", pk=vehicle_id)
#         return render(request, self.template_name, {"form": form_instance, "vehicle": vehicle})

# class PasswordResetView(View):
#     template_name = "password_reset.html"
#     form_class = PasswordResetForm

#     def get(self, request, *args, **kwargs):
#         form_instance = self.form_class()
#         return render(request, self.template_name, {"form": form_instance})

#     def post(self, request, *args, **kwargs):
#         form_instance = self.form_class(request.POST)
#         if form_instance.is_valid():
#             username = form_instance.cleaned_data.get("username")
#             email = form_instance.cleaned_data.get("email")
#             password1 = form_instance.cleaned_data.get("password1")
#             password2 = form_instance.cleaned_data.get("password2")
#             if password1 == password2:
#                 try:
#                     user = User.objects.get(username=username, email=email)
#                     user.set_password(password2)
#                     user.save()
#                     return redirect("signin")
#                 except User.DoesNotExist:
#                     messages.error(request, "Invalid username or email.")
#             else:
#                 messages.error(request, "Passwords do not match.")
#         return render(request, self.template_name, {"form": form_instance})



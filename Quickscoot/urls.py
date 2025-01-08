"""Quickscoot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from scoot import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/',views.SignUpView.as_view(),name='signup'),
    path('signin/',views.SignInView.as_view(),name='signin'),
    path("signout/",views.SignoutView.as_view(), name="signout"),
    path('owner-dashboard/', views.owner_dashboard_view, name='owner_dashboard'),

    path("profile/edit/",views.UserProfileEditView.as_view(), name="profile-edit"),
    path("profile/view/",views.UserProfileView.as_view(), name="profile-view"),

    path("renterprofile/edit/",views.RenterProfileEditView.as_view(), name="renterprofile-edit"),
    path("renterprofile/view/",views.RenterProfileView.as_view(), name="renterprofile-view"),

    path("aboutowner/",views.AboutUsView.as_view(), name="about-owner"),
    path("contactus/",views.ContactUsView.as_view(), name="contact-us"),

    path('renter-dashboard/', views.renter_dashboard_view, name='renter-dashboard'),
    path('vehicle/add/',views.TwoWheelerCreateView.as_view(),name="two-wheeler-add"),
    path('vehicle/list/',views.MyTwoWheelerListView.as_view(),name="two-wheeler-list"),
    path('vehicle/edit/<int:pk>/',views.TwoWheelerEditView.as_view(), name='two-wheeler-edit'),

    path('vehicle/delete/<int:pk>/',views.TwoWheelerDeleteView.as_view(), name='two-wheeler-delete'),

    #renter

    path('vehicleall/',views.VehicleListView.as_view(),name="vehicle-all"),

    path('vehicle/<int:pk>/', views.SeeVehicleDetailView.as_view(), name='vehiclefull-detail'),


    # path('vehicle/<int:pk>/',views.ViewVehicleDetailView.as_view(), name='vehiclefull_detail'),
    # path('vehicle/<int:id>/', views.vehicle_full_detail, name='vehicle_full_detail'),
    # path('vehicle/<int:id>/', views.vehicle_full_detail, name='vehicle_full_detail'),
    # path('vehicle/<int:id>/', views.vehicle_full_detail, name='vehicle_full_detail'),
    # path('vehicle/<int:vehicle_id>/', views.vehicle_full_detail, name='vehicle_full_detail'),
    
    path('renter/date/',views.AvailableDateView.as_view(), name='select_dates'),
    # path('booking/<int:pk>/total-price/',views.TotalPriceView.as_view(), name='total-price'),
    path('vehicle/<int:pk>/total-price/',views.TotalPriceView.as_view(), name='total-price'),
    # path('checkout/<int:pk>/',views.CheckOutView.as_view(), name='checkout'),
    # path('checkout/',views.CheckOutView.as_view(), name='checkout'),
    # path('payment-verify/',views.PaymentVerification.as_view(), name='payment-verify'),
    #  path('orders/', views.MyOrderView.as_view(), name='my-orders'),


    #  path('checkout/<int:pk>/', views.CheckoutView.as_view(), name='checkout'),
    # .........
    path('book/<int:pk>/', views.BookVehicleView.as_view(), name='book_vehicle'),

    path('booking/success/<int:pk>/', views.BookingSuccessView.as_view(), name='booking_confirmation'),


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



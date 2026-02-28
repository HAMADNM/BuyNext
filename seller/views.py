from django.shortcuts import render,redirect
from core.models import User
from .models import *
from django.contrib import messages
from django.contrib.auth import login
from core.decorator import seller_profile_required,verified_seller_required

# Create your views here.
def user_seller_bridge(request):
    return render(request,"seller/user_seller_bridge.html")
def seller_registration(request):
    if request.method == "POST":
         store_name=request.POST.get("store_name")
         gst_number=request.POST.get("gst_number")
         description=request.POST.get("description")
         logo=request.FILES.get("logo")
         if SellerProfile.objects.filter(store_name=store_name).exists():
               messages.error(request, "This store name is already registered. Please choose a unique brand name.")
               return render(request,"seller/seller_registration.html",{"data":request.POST})
         if SellerProfile.objects.filter(gst_number=gst_number).exists():
               messages.error(request, "This GSTIN is already linked to an existing seller account. Please log in to your original account.")
               return render(request,"seller/seller_registration.html",{"data":request.POST})    
         if not  request.user.is_authenticated:
              first_name=request.POST.get("first_name")
              last_name=request.POST.get("last_name")
              username=request.POST.get("username")
              email = request.POST.get("email")
              phone_no = request.POST.get("phone_display")
              password = request.POST.get("password")
              confirm_password = request.POST.get("confirm_password")
              if username:
                   final_username=username
              elif first_name or last_name:
                   final_username =(first_name+last_name).lower()
              elif email:
                   final_username = email.split("@")[0].lower()

              else:
                   final_username = "user"
                 
              if password != confirm_password:
                    messages.error(request, "Passwords do not match")
                    return render(request,"seller/seller_registration.html",{"data":request.POST})
              if User.objects.filter(username=final_username).exists():
                    messages.error(request, "Username already taken")
                    return render(request,"seller/seller_registration.html",{"data":request.POST})
              if User.objects.filter(email=email).exists():
                    messages.error(request, "Email already registered")
                    return render(request,"seller/seller_registration.html",{"data":request.POST})
              if User.objects.filter( phone_number=phone_no).exists():
                    messages.error(request, "phone number already registered")
                    return render(request,"seller/seller_registration.html",{"data":request.POST})
              user=User.objects.create_user(
                    username=final_username,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone_number=phone_no,
                    password=password
                )
              user.is_active=True
              user.save()
              login(request, user)
         else:
              user=request.user
                
         seller_profile = SellerProfile.objects.create(
                user=user,
                store_name=store_name,
                gst_number = gst_number,
                description=description,
                logo=logo,
            )
         seller_profile.save()
         return redirect('seller_waiting_area')
    return render(request,"seller/seller_registration.html",{"data":request.POST})
@verified_seller_required
def seller_dashboard(request):
     return render(request,"seller/dashboard.html")
@verified_seller_required
def seller_products(request):
     return render(request,"seller/product.html")
@verified_seller_required
def add_products(request):
     return render(request,"seller/addproduct.html")
@verified_seller_required
def seller_inventory(request):
     return render(request,"seller/inventory.html")
@verified_seller_required
def seller_order(request):
     return render(request,"seller/seller_order.html")
@verified_seller_required
def seller_earnings(request):
     return render(request,"seller/earnings.html")
@verified_seller_required
def offer_discount(request):
     return render(request,"seller/offeranddiscount.html")
@verified_seller_required
def seller_reviews(request):
     return render(request,"seller/sellerreviews.html")
@seller_profile_required
def seller_profile(request):
    profile = request.user.seller_profile

    if request.method == "POST":
        profile.store_name = request.POST.get("store_name")
        profile.description = request.POST.get("description")

        if request.FILES.get("logo"):
            profile.logo = request.FILES.get("logo")

        if request.FILES.get("banner"):
            profile.banner = request.FILES.get("banner")

        profile.save()

    return render(request, "seller/sellerprofile.html", {
        "profile": profile
    })
@verified_seller_required
def seller_settings(request):
     return render(request,"seller/seller_settings.html")
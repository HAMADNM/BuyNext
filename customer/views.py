from django.shortcuts import render,redirect,get_object_or_404
from core.models import *
from seller.models import *
from .models import *
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from core.decorator import customer_required
import razorpay
from django.db import transaction
from django.db.models import F


# Create your views here.
@customer_required
def user_profile_view(request):
    user_obj = request.user

    if request.method == "POST":

        user_obj.first_name = request.POST.get("firstname")
        user_obj.last_name = request.POST.get("lastname")

        new_email = request.POST.get("email")
        if new_email and new_email != user_obj.email:
            if User.objects.filter(email=new_email).exclude(id=user_obj.id).exists():
                messages.error(request, "Email already exists")
                return redirect("profile")

            user_obj.email = new_email
            user_obj.is_email_verified = False  

        new_phone = request.POST.get("phone_number")
        if new_phone and new_phone != user_obj.phone_number:
            if User.objects.filter(phone_number=new_phone).exclude(id=user_obj.id).exists():
                messages.error(request, "Phone number already exists")
                return redirect("profile")

            user_obj.phone_number = new_phone
            user_obj.is_phone_verified = False  

        pro_image = request.FILES.get("profile_image")
        if pro_image:
            if user_obj.profile_image:
                user_obj.profile_image.delete(save=False)
            user_obj.profile_image = pro_image

        user_obj.save()

        messages.success(request, "Profile updated. Please verify updated details if changed.")
        return redirect("profile")

    addresses = Address.objects.filter(user=request.user)

    context = {
        "addresses": addresses,
        "user": user_obj,
    }

    return render(request, "customer/profile.html", context)
@customer_required
def set_default_address(request,address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
    address.is_default = True
    address.save()
    messages.success(request, "Default address updated")
    return redirect("profile")
@customer_required
def delete_address(request,address_id):
    address =get_object_or_404(Address,user=request.user,id=address_id)
    address.delete()
    messages.error(request,"Address deleted successfully")
    return redirect("profile")

@customer_required
def save_address(request):

    if request.method == "POST":

        address_id = request.POST.get("address_id")

        full_name = request.POST.get("full_name")
        phone_number = request.POST.get("phone_number")
        pincode = request.POST.get("pincode")
        locality = request.POST.get("locality")
        house_info = request.POST.get("house_info")
        city = request.POST.get("city")
        state = request.POST.get("state")
        country = request.POST.get("country")
        landmark = request.POST.get("landmark")
        address_type = request.POST.get("address_type")
        is_default = request.POST.get("is_default") == "on"
        if is_default:
            Address.objects.filter(user=request.user, is_default=True).update(is_default=False)

        if address_id:
            address = get_object_or_404(Address, id=address_id, user=request.user)
        else:
            address = Address(user=request.user)

        address.full_name = full_name
        address.phone_number = phone_number
        address.pincode = pincode
        address.locality = locality
        address.house_info = house_info
        address.city = city
        address.state = state
        address.country = country
        address.landmark = landmark
        address.address_type = address_type
        address.is_default = is_default

        address.save()

        messages.success(request, "Address saved successfully")
    if request.GET.get("next") == "checkout":
        return redirect("checkout")

    return redirect("profile")
    
@customer_required
def add_cart(request,variant_id):
    MAX_CART_QUANTITY = 3
    variant=get_object_or_404(
        ProductVariant.objects.select_related("product"),
        id=variant_id,product__is_active=True,
        product__approval_status="APPROVED"
    )
    
    if variant.stock_quantity < 1:
        return JsonResponse({'status':'error','message':'Out of Stock'},status=400)
    cart, created= Cart.objects.get_or_create(user=request.user)
    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        variant=variant,
        defaults={'price_at_time': variant.selling_price}
    )

    if not item_created:
        if cart_item.quantity >= MAX_CART_QUANTITY:
            return JsonResponse({
                'status': 'error',
                'message': 'Maximum 3 items allowed per product'
            }, status=400)
        if cart_item.quantity < variant.stock_quantity:
            cart_item.quantity += 1
            cart_item.save()
        else:
            return JsonResponse({'status': 'error', 'message': 'Stock limit reached'}, status=400)
    cart_count = cart.items.count()


    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'cart_count': cart_count
        })
    return redirect("product_details",slug=variant.product.slug)
@customer_required
def view_cart(request):
    cart,created=Cart.objects.get_or_create(user=request.user)
    cart_items = (
    CartItem.objects
    .select_related("variant","variant__product","variant__product__seller")
    .prefetch_related("variant__images",
        "variant__variant_attributes__option__attribute"
    )
    .filter(cart=cart))
    
    context = {
        "cart": cart,
        "cart_items": cart_items
    }

    return render(request, "customer/cart.html", context)
@customer_required
def delete_cart_item(request,cart_item_id):
    if request.method == "POST":
        cart_item =get_object_or_404(CartItem.objects.select_related("cart"),id=cart_item_id,cart__user=request.user) 
        cart_item.delete()
        messages.success(request, "Item removed from cart successfully.")
    return redirect("view_cart")



@customer_required
def update_cart_item(request):
    MAX_CART_QUANTITY = 3

    if request.method == "POST":

        item_id = request.POST.get("item_id")
        action = request.POST.get("action")

        cart_item = get_object_or_404(
            CartItem.objects.select_related("variant", "cart"),
            id=item_id,
            cart__user=request.user
        )

        if action == "increase":
            if cart_item.quantity >= MAX_CART_QUANTITY:
                   messages.error(request, "Maximum 3 items allowed per product.")
            elif cart_item.quantity >= cart_item.variant.stock_quantity:
                messages.error(request, "Stock limit reached.")
            else:
                cart_item.quantity += 1
                cart_item.save()
                messages.success(request, "Quantity increased")

        elif action == "decrease":

            cart_item.quantity -= 1

            if cart_item.quantity <= 0:
                cart_item.delete()
                messages.success(request, "Item removed from cart")
                return redirect("view_cart")

            cart_item.save()
            messages.success(request, "Quantity decreased")

    return redirect("view_cart")
@customer_required
def add_wishlist(request,variant_id):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)
    variant=get_object_or_404(ProductVariant,id=variant_id)
    wishlist = Wishlist.objects.filter(user=request.user,is_default=True).first()
    if not wishlist:
            wishlist,created=Wishlist.objects.get_or_create(
             user=request.user,
             wishlist_name="Mywishlist",
             is_default=True,
        )
    wishlist_item = WishlistItem.objects.filter(
        wishlist=wishlist,
        variant=variant
    ).first()
    if wishlist_item:
        wishlist_item.delete()
        return JsonResponse({
            "status":"removed"
        })
    else:
        WishlistItem.objects.create(
            wishlist=wishlist,
            variant=variant
        )
        return JsonResponse({
            "status":"added"
        })
@customer_required
def view_wishlist(request):

    collections = Wishlist.objects.filter(
        user=request.user
    ).prefetch_related(
        "items__variant__product",
        "items__variant__product__seller",
        "items__variant__images",

    )

    collection_id = request.GET.get("collection")

    active_collection = None
    wishlist_items = None

    if collection_id:
        active_collection = collections.filter(id=collection_id).first()

    if not active_collection:
        active_collection = collections.filter(is_default=True).first()
    if not active_collection:
        active_collection = collections.first()

    if active_collection:
        wishlist_items = active_collection.items.select_related(
            "variant__product",
            "variant__product__seller"
        )

    context = {
        "collections": collections,
        "wishlist_items": wishlist_items,
        "active_collection": active_collection,
    }

    return render(request, "customer/wishlist.html", context)
@customer_required
def add_collection(request):

    if request.method != "POST":
        return  redirect("view_wishlist")

    name = request.POST.get("name")

    collection, created = Wishlist.objects.get_or_create(
        user=request.user,
        wishlist_name=name
    )

    if not created:
      messages.error(request, "Collection already exists")
      return redirect("view_wishlist")
    if not Wishlist.objects.filter(user=request.user, is_default=True).exists():
        collection.is_default = True
        collection.save()

    messages.success(request, "Collection created successfully")
    return redirect("view_wishlist")
@customer_required
def set_default_collection(request,collection_id):
     if request.method != "POST":
        return redirect("view_wishlist")
     collection=get_object_or_404(Wishlist,id=collection_id,user=request.user)
     Wishlist.objects.filter(user=request.user,is_default=True).update(is_default=False)
     collection.is_default=True
     collection.save()
     return redirect("view_wishlist")
@customer_required
def remove_wishlist_item(request, item_id):

    if request.method != "POST":
        return redirect("view_wishlist")

    item = get_object_or_404(
        WishlistItem,
        id=item_id,
        wishlist__user=request.user
    )

    item.delete()
    messages.success(request, "product removed successfully")

    return redirect("view_wishlist")
@customer_required
def remove_collection(request, collection_id):

    if request.method != "POST":
        return redirect("view_wishlist")

    collection = get_object_or_404(
        Wishlist,
        id=collection_id,
        user=request.user
    )

    was_default = collection.is_default

    collection.delete()

    if was_default:
        new_default = Wishlist.objects.filter(
            user=request.user,
            is_default=False
        ).first()

        if new_default:
            new_default.is_default = True
            new_default.save(update_fields=["is_default"])

    messages.success(request, "Collection deleted successfully")

    return redirect("view_wishlist")

@customer_required
def checkout_view(request):

    checkout_type = request.GET.get("type")

    if checkout_type == "buy_now":
        request.session["checkout_type"] = "buy_now"
        request.session["variant_id"] = request.GET.get("variant_id")
        request.session["quantity"] = int(request.GET.get("quantity", 1))

    elif checkout_type == "cart":
        request.session["checkout_type"] = "cart"

    checkout_type = request.session.get("checkout_type")

    items = []
    total = 0

    if checkout_type == "buy_now":

        variant_id = request.session.get("variant_id")
        quantity = request.session.get("quantity", 1)

        if not variant_id:
            messages.error(request, "Invalid product")
            return redirect("home")

        variant = ProductVariant.objects.get(id=variant_id)

        if quantity > 3:
            quantity = 3
            request.session["quantity"] = 3
            messages.warning(request, "Maximum 3 quantity allowed")

        subtotal = variant.selling_price * quantity
        total += subtotal

        items.append({
            "id": variant.id,   # ✅ FIXED
            "variant": variant,
            "quantity": quantity,
            "subtotal": subtotal
        })

    else:
        cart = Cart.objects.filter(user=request.user).first()

        if not cart:
            messages.warning(request, "Your cart is empty")
            return redirect("home")

        cart_items = CartItem.objects.filter(cart=cart)

        for item in cart_items:

            quantity = item.quantity

            if quantity > 3:
                quantity = 3
                item.quantity = 3
                item.save()
                messages.warning(request, "Max 3 quantity allowed per item")

            price = item.variant.selling_price
            subtotal = price * quantity

            total += subtotal

            items.append({
                "id": item.id,  
                "variant": item.variant,
                "quantity": quantity,
                "subtotal": subtotal
            })

    default_address = Address.objects.filter(
        user=request.user,
        is_default=True
    ).first()

    context = {
    "cart_items": items,
    "total_price": total, 
    "default_address": default_address,
    "checkout_type": checkout_type,
    "buy_now_item": items[0] if checkout_type == "buy_now" else None
    }

    return render(request, "customer/checkout.html", context)
@customer_required
def select_address(request):
    addresses = Address.objects.filter(user=request.user)

    return render(request, "customer/select_address_checkout.html", {
        "addresses": addresses
    })
@customer_required
def set_address(request, id):
    address = Address.objects.get(id=id, user=request.user)
    Address.objects.filter(user=request.user).update(is_default=False)
    address.is_default = True
    address.save()

    return redirect("checkout")

@customer_required
def add_address(request):
    return render(request, "customer/add_address.html")
@customer_required
def edit_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)

    return render(request, "customer/edit_address.html", {
        "address": address
    })



@customer_required
def place_order(request):

    if request.method != "POST":
        return redirect("all_products")

    user = request.user
    if not user.is_email_verified:
      messages.error(request, "Please verify your email before placing an order.")
      return redirect("profile")

    address = Address.objects.filter(user=user, is_default=True).first()

    if not address:
        messages.error(request, "Select delivery address.")
        return redirect("checkout")

    payment_method = request.POST.get("payment_method")
    is_buy_now = request.POST.get("is_buy_now") == "true"

    items = []
    if is_buy_now:
        variant_id = request.POST.get("variant_id")
        quantity = int(request.POST.get("quantity", 1))

        # Validate quantity
        if quantity < 1:
            quantity = 1
        elif quantity > 3:
            quantity = 3

        variant = ProductVariant.objects.select_related("product__seller").get(id=variant_id)
        if request.user.is_seller and variant.product.seller.user == request.user:
            messages.error(request, "You cannot buy your own product.")
            return redirect("all_products")

        items.append({
            "variant": variant,
            "quantity": quantity,
            "seller": variant.product.seller,
            "price": variant.selling_price
        })

    else:
        cart_items = CartItem.objects.filter(cart__user=user).select_related("variant__product__seller")

        if not cart_items.exists():
            return redirect("view_cart")

        for item in cart_items:

            new_qty = request.POST.get(f"quantity_{item.id}")
            quantity = int(new_qty) if new_qty else item.quantity

            # Validate quantity
            if quantity < 1:
                quantity = 1
            elif quantity > 3:
                quantity = 3
                
            if request.user.is_seller and item.variant.product.seller.user == request.user:
                messages.error(request, f"You cannot buy your own product: {item.variant.product.name}")
                return redirect("view_cart")

            items.append({
                "variant": item.variant,
                "quantity": quantity,
                "seller": item.variant.product.seller,
                "price": item.variant.selling_price
            })
    total = sum(i["price"] * i["quantity"] for i in items)
    try:
        with transaction.atomic():

            order = Order.objects.create(
                user=user,
                shipping_address=address,
                shipping_address_snapshot={
                    "name": address.full_name,
                    "phone": address.phone_number,
                    "city": address.city,
                    "state": address.state,
                    "pincode": address.pincode,
                    "house": address.house_info,
                },
                total_amount=total,
                final_amount=total,
                payment_method=payment_method,
                is_paid=False 
            )

            order_items = []

            for i in items:
                variant = i["variant"]
                quantity = i["quantity"]

                order_items.append(
                    OrderItem(
                        order=order,
                        variant=variant,
                        seller=i["seller"],
                        quantity=quantity,
                        price_at_purchase=i["price"]
                    )
                )

            OrderItem.objects.bulk_create(order_items)

            if payment_method == "COD":
                for item in order_items:
                    variant = item.variant

                    updated = ProductVariant.objects.filter(
                        id=variant.id,
                        stock_quantity__gte=item.quantity
                    ).update(stock_quantity=F('stock_quantity') - item.quantity)

                    if not updated:
                        messages.error(request, f"{variant.product.name} out of stock")
                        transaction.set_rollback(True)
                        return redirect("checkout")


                    InventoryLog.objects.create(
                        variant=variant,
                        change_amount=-item.quantity,
                        reason="PURCHASE",
                        reference_id=order.order_number,
                        note="Stock reduced for COD"
                    )

    except Exception as e:
        messages.error(request, str(e))
        return redirect("checkout")
    try:
        send_mail(
            "Order Confirmation - BuyNext",
            f"""
    Hi {user.username},

    Your order has been placed successfully!

    Order ID: {order.order_number}
    Total Amount: ₹{order.final_amount}

     Thank you for shopping with BuyNext!
""",
            settings.EMAIL_HOST_USER,
            [user.email]
        )
    except Exception as e:
        print("EMAIL ERROR:", e)
    if not is_buy_now:
        cart_items.delete()

    if payment_method == "COD":
        messages.success(request, "Order placed successfully!")
        return redirect("order_success", order_id=order.id)

    elif payment_method == "RAZORPAY":
        return redirect("razorpay_payment", order_id=order.id)
 

@customer_required
def razorpay_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.is_paid:
        messages.warning(request, "Order already paid.")
        return redirect("order_success", order_id=order.id)

    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )
    if order.razorpay_order_id:
        razorpay_order_id = order.razorpay_order_id
        amount = int(order.final_amount * 100)
    else:
        razorpay_order = client.order.create({
            "amount": int(order.final_amount * 100),
            "currency": "INR",
            "payment_capture": 1
        })

        razorpay_order_id = razorpay_order["id"]

        order.razorpay_order_id = razorpay_order_id
        order.save()

        amount = razorpay_order["amount"]

    context = {
        "order": order,
        "razorpay_order_id": razorpay_order_id,
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "amount": amount
    }

    return render(request, "customer/razorpay_payment.html", context)


@customer_required
def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    payment_id = request.GET.get("payment_id")
    razorpay_order_id = request.GET.get("order_id")
    signature = request.GET.get("signature")

    if not payment_id or not razorpay_order_id or not signature:
        messages.error(request, "Invalid payment response")
        return redirect("checkout")

    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    try:
        client.utility.verify_payment_signature({
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature
        })

        with transaction.atomic():

            order.is_paid = True
            order.payment_id = payment_id
            order.save()


            for item in order.items.select_related("variant"):
                variant = item.variant

                updated = ProductVariant.objects.filter(
                    id=variant.id,
                    stock_quantity__gte=item.quantity
                ).update(stock_quantity=F('stock_quantity') - item.quantity)

                if not updated:
                    raise Exception(f"{variant.product.name} out of stock")

                InventoryLog.objects.create(
                    variant=variant,
                    change_amount=-item.quantity,
                    reason="PURCHASE",
                    reference_id=order.order_number,
                    note="Stock reduced after Razorpay payment"
                )

        messages.success(request, "Payment successful!")
        return redirect("order_success", order_id=order.id)

    except Exception as e:
        print("Verification failed:", e)
        messages.error(request, "Payment verification failed!")
        return redirect("checkout")

@customer_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    return render(request, "customer/order_success.html", {
        "order": order
    })

@customer_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).prefetch_related(
        "items__variant__product",
        "items__variant__images",
        "items__seller"
    ).order_by("-ordered_at")
    
    context = {
        "orders": orders
    }
    
    return render(request, "customer/my_orders.html", context)

@customer_required
def order_details(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related(
            "items__variant__product",
            "items__variant__images",
            "items__seller"
        ),
        id=order_id,
        user=request.user
    )
    
    # Create address object from snapshot for template compatibility
    class AddressSnapshot:
        def __init__(self, data):
            self.full_name = data.get('name', '')
            self.phone_number = data.get('phone', '')
            self.house_info = data.get('house', '')
            self.locality = data.get('locality', '')
            self.city = data.get('city', '')
            self.state = data.get('state', '')
            self.pincode = data.get('pincode', '')
    
    order.address = AddressSnapshot(order.shipping_address_snapshot)
    order.payment_status = 'PAID' if order.is_paid else 'PENDING'
    
    context = {
        "order": order,
        "order_items": order.items.all()
    }
    
    return render(request, "customer/order_details.html", context)

@customer_required
def cancel_order_item(request, item_id):
    if request.method != "POST":
        return redirect("my_orders")
    
    order_item = get_object_or_404(OrderItem, id=item_id)
    if order_item.order.user != request.user:
        messages.error(request, "Unauthorized access")
        return redirect("my_orders")

    if order_item.item_status not in ['PLACED', 'CONFIRMED']:
        messages.error(request, "This item cannot be cancelled in its current status")
        return redirect("my_orders")
    if not order_item.variant.product.is_cancellable:
        messages.error(request, "This product cannot be cancelled")
        return redirect("my_orders")
    
    try:
        order_item.item_status = 'CANCELLED'
        order_item.save()
        
        order_item.variant.stock_quantity += order_item.quantity
        order_item.variant.save()
        
        InventoryLog.objects.create(
            variant=order_item.variant,
            change_amount=order_item.quantity,
            reason="CANCELLED",
            reference_id=order_item.order.order_number,
            note="Stock restored due to order cancellation"
        )
        
        messages.success(request, f"Item {order_item.variant.product.name} has been cancelled successfully")
    except Exception as e:
        messages.error(request, f"Error cancelling item: {str(e)}")
    
    return redirect("order_details", order_id=order_item.order.id)

@customer_required
def return_order_item(request, item_id):
    if request.method != "POST":
        return redirect("my_orders")
    
    order_item = get_object_or_404(OrderItem, id=item_id)
    
    if order_item.order.user != request.user:
        messages.error(request, "Unauthorized access")
        return redirect("my_orders")
    
    if order_item.item_status != 'DELIVERED':
        messages.error(request, "Only delivered items can be returned")
        return redirect("my_orders")
    
    if not order_item.variant.product.is_returnable:
        messages.error(request, "This product cannot be returned")
        return redirect("my_orders")
    
    try:
        order_item.item_status = 'RETURN_REQUESTED'
        order_item.save()
        
        send_mail(
            "Return Request Received - BuyNext",
            f"""
Hi {request.user.username},

We've received your return request for:

Product: {order_item.variant.product.name}
Order ID: {order_item.order.order_number}
Quantity: {order_item.quantity}

Our team will review your request and contact you soon with pickup details.

Thank you for shopping with BuyNext!
""",
            settings.EMAIL_HOST_USER,
            [request.user.email]
        )
        
        messages.success(request, f"Return request for {order_item.variant.product.name} has been submitted successfully. We'll contact you soon.")
    except Exception as e:
        messages.error(request, f"Error submitting return request: {str(e)}")
    
    return redirect("order_details", order_id=order_item.order.id)

@customer_required
def add_review(request, product_slug):
    
    product = get_object_or_404(Product, slug=product_slug)
    
    existing_review = Review.objects.filter(user=request.user, product=product).first()
    if existing_review:
        messages.info(request, "You have already reviewed this product.")
        return redirect("product_details", slug=product_slug)
    
    # Check if user has purchased this product
    user_order_items = OrderItem.objects.filter(
        order__user=request.user,
        variant__product=product
    )
    
    if not user_order_items.exists():
        messages.error(request, "You need to buy this item before you can review it.")
        return redirect("product_details", slug=product_slug)
    
    # Check if any order item is delivered
    delivered_items = user_order_items.filter(item_status='DELIVERED')
    if not delivered_items.exists():
        messages.error(request, "The product needs to be delivered before you can review it.")
        return redirect("product_details", slug=product_slug)
    
    if request.method == "POST":
        rating = request.POST.get("rating")
        title = request.POST.get("title", "").strip()
        comment = request.POST.get("comment", "").strip()
        images = request.FILES.getlist("images")
        
        if not rating or not comment:
            messages.error(request, "Rating and review comment are required.")
            return redirect("add_review", product_slug=product_slug)
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError("Invalid rating")
        except (ValueError, TypeError):
            messages.error(request, "Invalid rating value.")
            return redirect("add_review", product_slug=product_slug)
        

        # Create the review
        try:
            review = Review.objects.create(
                user=request.user,
                product=product,
                rating=rating,
                title=title,
                comment=comment,
                is_verified_purchase=True  # Since we verified delivery above
            )
        except Exception as e:
            messages.error(request, "Unable to create review. You may have already reviewed this product.")
            return redirect("product_details", slug=product_slug)
        
        for image in images[:5]: 
            try:
                ReviewImage.objects.create(review=review, image=image)
            except Exception as e:
                print(f"Error creating review image: {e}")
                continue
        
        messages.success(request, "Your review has been submitted successfully!")
        return redirect("product_details", slug=product_slug)
    
    context = {
        "product": product
    }
    return render(request, "customer/add_review.html", context)

@customer_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    product = review.product
    
    if request.method == "POST":
        rating = request.POST.get("rating")
        title = request.POST.get("title", "").strip()
        comment = request.POST.get("comment", "").strip()
        delete_images = request.POST.getlist("delete_images")
        new_images = request.FILES.getlist("images")
        
        if not rating or not comment:
            messages.error(request, "Rating and review comment are required.")
            return redirect("edit_review", review_id=review_id)
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError("Invalid rating")
        except (ValueError, TypeError):
            messages.error(request, "Invalid rating value.")
            return redirect("edit_review", review_id=review_id)
        review.rating = rating
        review.title = title
        review.comment = comment
        review.save()
        review.images.all().delete()

        for image in new_images[:5]:
            try:
                ReviewImage.objects.create(review=review, image=image)
            except Exception as e:
               
                print(f"Error creating review image: {e}")
                continue
        
        messages.success(request, "Your review has been updated successfully!")
        return redirect("product_details", slug=product.slug)
    
    context = {
        "review": review,
        "product": product
    }
    return render(request, "customer/edit_review.html", context)

@customer_required
def track_order_item(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related(
            "items__variant__product",
            "items__variant__images",
            "items__seller"
        ),
        id=order_id,
        user=request.user
    )
    
    class AddressSnapshot:
        def __init__(self, data):
            self.full_name = data.get('name', '')
            self.phone_number = data.get('phone', '')
            self.house_info = data.get('house', '')
            self.locality = data.get('locality', '')
            self.city = data.get('city', '')
            self.state = data.get('state', '')
            self.pincode = data.get('pincode', '')
    
    order.address = AddressSnapshot(order.shipping_address_snapshot)
    
    context = {
        "order": order,
        "order_items": order.items.all()
    }
    
    return render(request, "customer/track_item.html", context)



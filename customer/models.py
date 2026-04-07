import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import *
from seller.models import *
from seller.models import Product, ProductVariant, SellerProfile


class Cart(models.Model):
  
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"Cart of {self.user.username}"

    @property
    def total_items(self):
        return self.items.aggregate(total=models.Sum('quantity'))['total'] or 0

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())


class CartItem(models.Model):
   
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.CASCADE, related_name='cart_items'
    )
    quantity = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Must be at least 1"
    )
    price_at_time = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Snapshot of selling_price when item was added"
    )
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['cart', 'variant']]
        indexes = [
            models.Index(fields=['cart', 'variant']),
        ]

    def __str__(self):
        return f"{self.quantity}x {self.variant.sku_code} in {self.cart.user.username}'s cart"

    @property
    def subtotal(self):
        return self.price_at_time * self.quantity


class Wishlist(models.Model):
  
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlists')
    wishlist_name = models.CharField(max_length=100, default='My Wishlist')
    is_default = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False, help_text="Allow sharing via link")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['user', 'wishlist_name']]
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.user.username} — {self.wishlist_name}"


class WishlistItem(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.CASCADE, related_name='wishlist_items'
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['wishlist', 'variant']]
        ordering = ['-added_at']
        indexes = [
            models.Index(fields=['wishlist', 'variant']),
        ]

    def __str__(self):
        return f"{self.variant.sku_code} in {self.wishlist.wishlist_name}"


class Review(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    title = models.CharField(max_length=150, blank=True, help_text="Short review headline")
    comment = models.TextField()
    is_verified_purchase = models.BooleanField(
        default=False,
        help_text="True if this user actually ordered this product"
    )
    is_approved = models.BooleanField(default=True, help_text="Admin moderation flag")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['user', 'product']]
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'is_approved']),
            models.Index(fields=['product', 'rating']),
            models.Index(fields=['user', 'product']),
        ]

    def __str__(self):
        return f"{self.user.username} → {self.product.name} ({self.rating}★)"

class ReviewImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    review = models.ForeignKey(
        "customer.Review",
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = models.ImageField(upload_to="review_images/")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.review.id}"


class Order(models.Model):
  
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=100, unique=True, blank=True)

    shipping_address = models.ForeignKey(
        Address, on_delete=models.SET_NULL, null=True, blank=True
    )

    shipping_address_snapshot = models.JSONField()

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2)

    payment_method = models.CharField(max_length=50, blank=True)
    is_paid = models.BooleanField(default=False)
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    payment_id = models.CharField(max_length=255, blank=True, null=True)
    payment_signature = models.CharField(max_length=255, blank=True, null=True)

    note = models.TextField(blank=True)

    ordered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.order_number} — {self.user.username}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    


class OrderItem(models.Model):
     
    ITEM_STATUS = (
        ('PLACED', 'Placed'),
        ('CONFIRMED', 'Confirmed'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
        ('RETURN_REQUESTED', 'Return Requested'),
        ('RETURNED', 'Returned'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey(
        "seller.ProductVariant",
        on_delete=models.SET_NULL,
        null=True,
        related_name='order_items'
    )

    seller = models.ForeignKey(
        "seller.SellerProfile",
        on_delete=models.SET_NULL,
        null=True,
        related_name='order_items'
    )

    quantity = models.IntegerField(
        validators=[MinValueValidator(1)]
    )

    price_at_purchase = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price locked at purchase time"
    )

    item_status = models.CharField(
        max_length=30,
        choices=ITEM_STATUS,
        default='PLACED',
        db_index=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['order', 'item_status']),
            models.Index(fields=['seller', 'item_status']),
        ]

    def __str__(self):
        return f"{self.quantity}x {self.variant} ({self.item_status})"

    @property
    def subtotal(self):
        return self.price_at_purchase * self.quantity
    @property
    def display_status(self):
        return self.item_status.replace("_", " ").title()
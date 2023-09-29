import math

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.forms import ValidationError
from django_countries.fields import CountryField
from django.shortcuts import reverse
from django.utils.translation import gettext as _

from app import constants as const


class User(AbstractUser):
    """Model representing a user."""

    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    date_joined = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.username


class Coupon(models.Model):
    """Model representing a coupon."""

    code = models.CharField(max_length=15, unique=True)
    amount = models.FloatField()

    def __str__(self):
        return self.code

    def clean(self):
        if self.amount <= 0:
            raise ValidationError(_("Amount must be greater than 0."))


class Payment(models.Model):
    """Model representing a payment."""

    user = models.ForeignKey(User,
                             on_delete=models.SET_NULL,
                             blank=True,
                             null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    card_number = models.CharField(max_length=20)
    status = models.IntegerField(choices=const.PAYMENT_STATUS, default=0)

    def __str__(self):
        return self.user.username


class Address(models.Model):
    """Model representing an address."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=100)
    address_type = models.IntegerField(choices=const.ADDRESS_CHOICES,
                                       default=0)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'


class Item(models.Model):
    """Model representing an item."""

    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.IntegerField(choices=const.CATEGORY_CHOICES,
                                   default=0)
    label = models.IntegerField(choices=const.LABEL_CHOICES,
                                default=0)
    slug = models.SlugField()
    description = models.TextField()
    image = models.ImageField()
    is_deleted = models.BooleanField(default=False)
    overall = models.FloatField(default=0)
    purchases = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    def discount_percent(self):
        return 100 - self.discount_price/self.price * 100

    def round_up_overall(self):
        return math.ceil(self.overall)

    def get_absolute_url(self):
        return reverse("app:product", kwargs={
            'slug': self.slug
        })

    def get_add_to_cart_url(self):
        return reverse("app:add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("app:remove-from-cart", kwargs={
            'slug': self.slug
        })

    def get_remove_single_item_from_cart_url(self):
        return reverse("app:remove-single-item-from-cart", kwargs={
            'slug': self.slug
        })
    
    def is_liked_by_user(self, user):
        """Check if the item is liked by the given user."""
        try:
            # Kiểm tra xem có bản ghi trong bảng ViewHistory tương ứng với item và user này không
            view_history = ViewHistory.objects.get(user=user, item=self)
            return view_history.liked
        except ViewHistory.DoesNotExist:
            return False

class Order(models.Model):
    """Model representing an order."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    order_status = models.IntegerField(choices=const.ORDER_STATUS,
                                       default=0)
    refund_status = models.IntegerField(choices=const.REFUND_STATUS,
                                        default=0)
    coupon = models.ForeignKey(
        Coupon, on_delete=models.SET_NULL, blank=True, null=True)
    shipping_address = models.ForeignKey(
        Address,
        related_name='shipping_address',
        on_delete=models.SET_NULL,
        blank=True,
        null=True)
    billing_address = models.ForeignKey(
        Address,
        related_name='billing_address',
        on_delete=models.SET_NULL,
        blank=True,
        null=True)
    payment = models.ForeignKey(
        Payment, on_delete=models.SET_NULL, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now=True)
    amount = models.FloatField(default=0)

    def __str__(self):
        return self.user.username


class OrderItem(models.Model):
    """Model represent a item in order."""

    price = models.FloatField(default=0)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_single_price(self):
        if self.item.discount_price:
            return self.item.discount_price
        return self.item.price

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return (self.item.price - self.item.discount_price) * self.quantity

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()


class Refund(models.Model):
    """Model representing a refund."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"


class ShopInfor(models.Model):
    """Model representing the information about shop."""

    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1023)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    logo = models.ImageField()
    insta = models.CharField(max_length=255, blank=True, null=True)
    facebook = models.CharField(max_length=255, blank=True, null=True)
    youtube = models.CharField(max_length=255, blank=True, null=True)
    settings = models.CharField(max_length=2047, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Shop Information")
        verbose_name_plural = _("Shop Information")

    def save(self, *args, **kwargs):
        # Check if there is an existing record
        existing_record = ShopInfor.objects.first()
        if existing_record:
            # Update the existing record
            self.pk = existing_record.pk
        super().save(*args, **kwargs)


class ViewHistory(models.Model):
    """model representing the user's item viewing history."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    liked = models.BooleanField()
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} - {self.item.title}'


class Review(models.Model):
    """Model representing a user's review about an item."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    description = models.CharField(max_length=1023)
    overall = models.IntegerField()
    date_reviewed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username}: {self.item.title} - {self.overall} star'

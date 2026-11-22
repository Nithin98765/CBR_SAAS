
from django.conf import settings
from django.db import models


class Advertisement(models.Model):

    # Advertisement categories
    CATEGORY_CHOICES = [
        ("property", "Properties"),
        ("car", "Cars"),
        ("bike", "Bikes"),
        ("electronics", "Electronics"),
        ("appliances", "Appliances"),
        ("services", "Home Services"),
        ("interior", "Interior Design"),
    ]

    # Advertisement status
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("pending", "Pending"),
        ("published", "Published"),
        ("rejected", "Rejected"),
        ("sold", "Sold"),
    ]

    # Seller information
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="advertisements",
    )

    # Basic advertisement details
    title = models.CharField(max_length=200)
    description = models.TextField()

    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
    )

    # Pricing
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    negotiable = models.BooleanField(default=False)

    # Location details
    state = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    city = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    locality = models.CharField(
        max_length=150,
        blank=True,
        default="",
    )

    pincode = models.CharField(
        max_length=6,
        blank=True,
        default="",
    )

    # Contact details
    contact_name = models.CharField(
        max_length=150,
        blank=True,
        default="",
    )

    contact_mobile = models.CharField(
        max_length=16,
        blank=True,
        default="",
    )

    # Dynamic category-specific information
    # Example: brand, model, year, bedrooms, bathrooms
    attributes = models.JSONField(
        default=dict,
        blank=True,
    )

    # Advertisement publishing status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="published",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["status", "-created_at"],
                name="ad_status_created_idx",
            ),
            models.Index(
                fields=["category", "status"],
                name="ad_category_status_idx",
            ),
        ]

    def __str__(self):
        return f"{self.title} - {self.category}"


class AdvertisementImage(models.Model):

    advertisement = models.ForeignKey(
        Advertisement,
        on_delete=models.CASCADE,
        related_name="images",
    )

    image = models.ImageField(
        upload_to="advertisements/",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Image for {self.advertisement.title}"

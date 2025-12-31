from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Service(models.Model):
    """Model for cleaning services"""
    ICON_CHOICES = [
        ('🏠', 'House'),
        ('🏢', 'Building'),
        ('✨', 'Sparkles'),
        ('🪟', 'Window'),
        ('🏗️', 'Construction'),
        ('🧹', 'Broom'),
    ]
    
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=10, choices=ICON_CHOICES, default='🏠')
    price = models.CharField(max_length=50, help_text="e.g., 'From £25/hour'")
    description = models.TextField()
    feature_1 = models.CharField(max_length=100)
    feature_2 = models.CharField(max_length=100)
    feature_3 = models.CharField(max_length=100)
    feature_4 = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.name


class Testimonial(models.Model):
    """Model for customer testimonials"""
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100, help_text="e.g., London, UK")
    rating = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    text = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.location}"
    
    def get_initials(self):
        """Get initials for avatar"""
        names = self.name.split()
        if len(names) >= 2:
            return f"{names[0][0]}{names[1][0]}".upper()
        return names[0][0].upper()
    
    def get_stars(self):
        """Return star string"""
        return '★' * self.rating


class QuoteRequest(models.Model):
    """Model for quote/contact requests"""
    SERVICE_CHOICES = [
        ('residential', 'Residential Cleaning'),
        ('commercial', 'Commercial Cleaning'),
        ('carpet', 'Carpet & Upholstery'),
        ('windows', 'Window Cleaning'),
        ('construction', 'Post-Construction'),
        ('specialist', 'Specialist Services'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('quoted', 'Quoted'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    service = models.CharField(max_length=20, choices=SERVICE_CHOICES)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_service_display()} - {self.created_at.strftime('%Y-%m-%d')}"


class SiteSettings(models.Model):
    """Model for site-wide settings"""
    phone = models.CharField(max_length=20, default='0800 123 4567')
    email = models.EmailField(default='info@spotlessmop.co.uk')
    address = models.CharField(max_length=200, default='Nationwide UK Service')
    hours = models.TextField(default='Mon-Sat: 7am-8pm\nSunday: 9am-6pm')
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    
    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'
    
    def __str__(self):
        return "Site Settings"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
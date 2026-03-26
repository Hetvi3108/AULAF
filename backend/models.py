from django.db import models
from django.contrib.auth.models import User

STATUS_CHOICES = [
    ("Not Collected", "Not Collected"),
    ("Collected", "Collected"),
]

SUBMISSION_CHOICES = [
    ("desk", "Submitted to Lost & Found Desk"),
    ("finder", "Kept with Finder"),
]

LOCATION_CHOICES = [
    ("SAS", "School of Arts and Sciences"),
    ("GICT", "GICT Building"),
    ("UC", "University Center"),
    ("BK", "BK School Area"),
]




class Item(models.Model):
    item_name       = models.CharField(max_length=100)
    image           = models.ImageField(upload_to="items/")
    description     = models.TextField(blank=True, null=True)
    
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Not Collected")
    submission_type = models.CharField(max_length=20, choices=SUBMISSION_CHOICES)
    submitted_at    = models.CharField(max_length=10, choices=LOCATION_CHOICES, blank=True, null=True)
    reported_by     = models.ForeignKey(User, on_delete=models.CASCADE)
    date_reported   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.item_name


class Claim(models.Model):
    item            = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="claims")
    claimer_name    = models.CharField(max_length=100)
    enrollment_no   = models.CharField(max_length=50)
    au_email        = models.EmailField()
    id_card_photo   = models.ImageField(upload_to="claims/")
    claimed_at      = models.DateTimeField(auto_now_add=True)
    filled_by       = models.ForeignKey(User, on_delete=models.CASCADE, related_name="claims_filled")

    def __str__(self):
        return f"{self.claimer_name} - {self.item.item_name}"
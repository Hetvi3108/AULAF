from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
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
COMPLAINT_STATUS_CHOICES = [
    ("Pending",   "Pending"),
    ("Reviewing", "Reviewing"),
    ("Resolved",  "Resolved"),
    ("Rejected",  "Rejected"),
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
    audio_blob       = models.FileField(upload_to='audio/', blank=True, null=True)
    audio_transcript = models.TextField(blank=True, null=True)

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
    audio_file = models.FileField(upload_to='audio/', null=True, blank=True)
    def __str__(self):
        return f"{self.claimer_name} - {self.item.item_name}"






class Complaint(models.Model):
    STATUS_CHOICES = [
        ('pending',  'Pending'),
        ('reviewed', 'Under Review'),
        ('resolved', 'Resolved'),
        ('closed',   'Closed'),
    ]

    CATEGORY_CHOICES = [
        ('lost_item',  'Lost Item Not Listed'),
        ('found_item', 'Found Item Issue'),
        ('staff',      'Staff Behaviour'),
        ('process',    'Process/System Issue'),
        ('other',      'Other'),
    ]

    submitted_by      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints')
    name              = models.CharField(max_length=100, verbose_name="Full Name")
    user_email        = models.EmailField(verbose_name="Email ID")
    enrollment_number = models.CharField(max_length=20, verbose_name="Enrollment Number")
    related_item      = models.ForeignKey(Item, on_delete=models.SET_NULL,
                                          null=True, blank=True, related_name='complaints')
    subject           = models.CharField(max_length=200, default="General Complaint")
    category          = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    status            = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    staff_remarks     = models.TextField(blank=True)
    created_at        = models.DateTimeField(auto_now_add=True,null=True)
    updated_at        = models.DateTimeField(auto_now=True,null=True)

    class Meta:
        ordering     = ['-created_at']
        verbose_name = 'Complaint'
        verbose_name_plural = 'Complaints'

    def __str__(self):
        return f"[{self.get_status_display()}] {self.subject} — {self.submitted_by.username}"
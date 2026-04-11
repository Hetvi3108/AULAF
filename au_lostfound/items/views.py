from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from .models import Item, Claim, Complaint
from .forms import AURegisterForm, ItemForm, ClaimForm, ComplaintForm
import os
import torch
import numpy as np
from PIL import Image as PILImage
from transformers import CLIPProcessor, CLIPModel
#from sklearn.metrics.pairwise import cosine_similarity
#import whisper
from django.db.models import Q

# Load models once globally
clip_model     = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
#whisper_model  = whisper.load_model("base")
# -------------------------------
# AUTH
# -------------------------------
def register(request):
    form = AURegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("login")
    return render(request, "items/register.html", {"form": form})


def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, "items/login.html", {"error": "Invalid credentials"})

        user = authenticate(request, username=user_obj.username, password=password)
        if user:
            login(request, user)
            return redirect("home")

    return render(request, "items/login.html")


def user_logout(request):
    logout(request)
    return redirect("login")


# -------------------------------
# HOME
# -------------------------------
@login_required
def home(request):
    items = Item.objects.all().order_by("-date_reported")

    return render(request, "items/home.html", {
        "items": items,
        "total_items": items.count(),
        "not_collected": items.filter(status="Not Collected").count(),
        "collected_items": items.filter(status="Collected").count(),
    })


# -------------------------------
# ITEM CRUD
# -------------------------------
@login_required
def add_item(request):
    form = ItemForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and form.is_valid():
        item = form.save(commit=False)
        item.reported_by = request.user
        item.status = "Not Collected"
        item.save()
        return redirect("home")

    return render(request, "items/add_item.html", {"form": form})


@login_required
def item_detail(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    return render(request, "items/item_detail.html", {"item": item})


@login_required
def update_status(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    item.status = "Collected" if item.status == "Not Collected" else "Not Collected"
    item.save()
    return redirect("home")


# -------------------------------
# CLAIM
# -------------------------------
@login_required
def claim_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    if request.user != item.reported_by:
        return render(request, "items/error.html", {"message": "Not authorized"})

    form = ClaimForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and form.is_valid():
        claim = form.save(commit=False)
        claim.item = item
        claim.filled_by = request.user
        claim.save()

        item.status = "Collected"
        item.save()

        return redirect("item_detail", item_id=item.id)

    return render(request, "items/claim_item.html", {"form": form, "item": item})


# -------------------------------
# MY ITEMS
# -------------------------------
@login_required
def my_items(request):
    items = Item.objects.filter(reported_by=request.user)
    return render(request, "items/my_items.html", {"items": items})


# -------------------------------
# SUBMIT COMPLAINT
# -------------------------------
@login_required
def submit_complaint(request, item_id=None):
    item = None
    if item_id:
        item = get_object_or_404(Item, id=item_id)

    if request.method == "POST":
        form = ComplaintForm(request.POST)
        if form.is_valid():
            complaint              = form.save(commit=False)
            complaint.submitted_by = request.user
            complaint.related_item = item
            # auto-set subject and category
            complaint.subject  = f"Complaint regarding: {item.item_name}" if item else "General Complaint"
            complaint.category = "other"
            complaint.save()

            _send_complaint_to_admin(complaint, item)
            _send_complaint_confirm_to_student(complaint, item)

            return redirect("complaint_success")
    else:
        form = ComplaintForm(initial={
            "name":       request.user.get_full_name() or "",
            "user_email": request.user.email or "",
        })

    return render(request, "items/complaint_submit.html", {
        "form": form,
        "item": item,
    })


def _send_complaint_to_admin(complaint, item):
    admin_email = getattr(settings, "COMPLAINT_HANDLER_EMAIL", None)
    if not admin_email:
        return

    item_block = ""
    if item:
        item_block = f"""
━━━━━━━━━━━━━━━━━━━━━━━━
ITEM DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━

Item Name      : {item.item_name}
Description    : {item.description or "N/A"}
Location       : {item.get_submitted_at_display() if item.submitted_at else "N/A"}
Submission Type: {item.get_submission_type_display()}
Date Reported  : {item.date_reported.strftime("%d %b %Y, %I:%M %p")}
Item ID        : #{item.id}
Reported By    : {item.reported_by.username} ({item.reported_by.email})
"""

    # Fetch the claimer's email for this item (if a claim exists)
    claimer_email_block = ""
    if item:
        claim = item.claims.order_by("-claimed_at").first()
        if claim:
            claimer_email_block = f"\nClaimer Email  : {claim.au_email}"

    subject = f"[AULAF] New Complaint #{complaint.id} — by {complaint.name}"
    message = f"""A new complaint has been submitted on AULAF.

━━━━━━━━━━━━━━━━━━━━━━━━
STUDENT INFORMATION
━━━━━━━━━━━━━━━━━━━━━━━━

Name           : {complaint.name}
Email ID       : {complaint.user_email}
Enrollment No  : {complaint.enrollment_number}
Submitted On   : {complaint.created_at.strftime("%d %b %Y, %I:%M %p")}
{claimer_email_block}
{item_block}
━━━━━━━━━━━━━━━━━━━━━━━━

Please review this complaint in the admin panel.

Regards,
AULAF – Automated Notification
"""
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin_email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"[AULAF Complaint] Admin email failed: {e}")


def _send_complaint_confirm_to_student(complaint, item):
    item_block = ""
    if item:
        item_block = f"""
━━━━━━━━━━━━━━━━━━━━━━━━
RELATED ITEM
━━━━━━━━━━━━━━━━━━━━━━━━

Item Name      : {item.item_name}
Description    : {item.description or "N/A"}
Location       : {item.get_submitted_at_display() if item.submitted_at else "N/A"}
"""

    subject = f"[AULAF] Your Complaint #{complaint.id} Has Been Received"
    message = f"""Dear {complaint.name},

Your complaint has been successfully submitted to AULAF (Ahmedabad University Lost & Found).

━━━━━━━━━━━━━━━━━━━━━━━━
YOUR INFORMATION
━━━━━━━━━━━━━━━━━━━━━━━━

Name           : {complaint.name}
Email ID       : {complaint.user_email}
Enrollment No  : {complaint.enrollment_number}
Submitted On   : {complaint.created_at.strftime("%d %b %Y, %I:%M %p")}
{item_block}
━━━━━━━━━━━━━━━━━━━━━━━━

Our team will review your complaint and respond shortly.

Regards,
AULAF – Ahmedabad University Lost and Found
"""
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[complaint.user_email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"[AULAF Complaint] Student email failed: {e}")


# -------------------------------
# MY COMPLAINTS
# -------------------------------
@login_required
def my_complaints(request):
    complaints = Complaint.objects.filter(submitted_by=request.user).order_by("-created_at")
    return render(request, "items/complain_list.html", {"complaints": complaints})


# -------------------------------
# COMPLAINT SUCCESS
# -------------------------------
@login_required
def complaint_success(request):
    return render(request, "items/complaint_success.html")

@login_required
def complaint_detail_view(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk, submitted_by=request.user)
    return render(request, "items/complaint_detail.html", {"complaint": complaint})
# -------------------------------
# ITEM EDIT / DELETE
# -------------------------------
@login_required
def edit_item(request, item_id):
    item = get_object_or_404(Item, id=item_id, reported_by=request.user)
    form = ItemForm(request.POST or None, request.FILES or None, instance=item)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("item_detail", item_id=item.id)
    return render(request, "items/add_item.html", {"form": form})


@login_required
def delete_item(request, item_id):
    item = get_object_or_404(Item, id=item_id, reported_by=request.user)
    if request.method == "POST":
        item.delete()
        return redirect("home")
    return render(request, "items/confirm_delete.html", {"object": item})


# -------------------------------
# CLAIM EDIT / DELETE / VIEW
# -------------------------------
@login_required
def view_claims(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    claims = Claim.objects.filter(item=item)
    return render(request, "items/view_claims.html", {"item": item, "claims": claims})


@login_required
def edit_claim(request, claim_id):
    claim = get_object_or_404(Claim, id=claim_id)
    form = ClaimForm(request.POST or None, request.FILES or None, instance=claim)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("item_detail", item_id=claim.item.id)
    return render(request, "items/claim_item.html", {"form": form, "item": claim.item})


@login_required
def delete_claim(request, claim_id):
    claim = get_object_or_404(Claim, id=claim_id)
    item_id = claim.item.id
    if request.method == "POST":
        claim.delete()
        return redirect("item_detail", item_id=item_id)
    return render(request, "items/confirm_delete.html", {"object": claim})


# -------------------------------
# SEARCH
# -------------------------------
@login_required
def image_search(request):
    results = []
    if request.method == "POST" and request.FILES.get("query_image"):

        query_image = request.FILES["query_image"]
        temp_path = os.path.join(settings.MEDIA_ROOT, "temp_query.jpg")
        with open(temp_path, "wb+") as f:
            for chunk in query_image.chunks():
                f.write(chunk)

        try:
            img = PILImage.open(temp_path).convert("RGB")
            inputs = clip_processor(images=img, return_tensors="pt")
            with torch.no_grad():
                query_emb = clip_model.get_image_features(**inputs)
                query_emb = query_emb / query_emb.norm(dim=-1, keepdim=True)
                query_emb = query_emb.numpy()

            scored = []
            for item in Item.objects.exclude(image=""):
                item_path = os.path.join(settings.MEDIA_ROOT, str(item.image))
                if os.path.exists(item_path):
                    try:
                        i = PILImage.open(item_path).convert("RGB")
                        inp = clip_processor(images=i, return_tensors="pt")
                        with torch.no_grad():
                            emb = clip_model.get_image_features(**inp)
                            emb = emb / emb.norm(dim=-1, keepdim=True)
                            emb = emb.numpy()
                        score = cosine_similarity(query_emb, emb)[0][0]
                        print(f"Item: {item.item_name} | Score: {score:.4f}")
                        scored.append((score, item))
                    except Exception as e:
                        print(f"Skipped item {item.id}: {e}")
                        continue

            scored.sort(key=lambda x: x[0], reverse=True)

            # Show items above 0.5 threshold, max 5
            results = [item for score, item in scored[:5] if score > 0.5]

            # If nothing matched, show top 3 anyway
            if not results and scored:
                results = [item for score, item in scored[:3]]

        except Exception as e:
            print(f"Image search error: {e}")

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    return render(request, "items/image_search.html", {"results": results})

@login_required
def camera_search(request):
    matched_ids = []
    if request.method == "POST" and request.FILES.get("query_image"):
        temp_path = os.path.join(settings.MEDIA_ROOT, "temp_camera.jpg")
        with open(temp_path, "wb+") as f:
            for chunk in request.FILES["query_image"].chunks():
                f.write(chunk)
        try:
            img    = PILImage.open(temp_path).convert("RGB")
            inputs = clip_processor(images=img, return_tensors="pt")
            with torch.no_grad():
                query_emb = clip_model.get_image_features(**inputs)
                query_emb = query_emb / query_emb.norm(dim=-1, keepdim=True)
                query_emb = query_emb.numpy()

            scored = []
            for item in Item.objects.exclude(image=""):
                item_path = os.path.join(settings.MEDIA_ROOT, str(item.image))
                if os.path.exists(item_path):
                    try:
                        i   = PILImage.open(item_path).convert("RGB")
                        inp = clip_processor(images=i, return_tensors="pt")
                        with torch.no_grad():
                            emb = clip_model.get_image_features(**inp)
                            emb = emb / emb.norm(dim=-1, keepdim=True)
                            emb = emb.numpy()
                        score = float(cosine_similarity(query_emb, emb)[0][0])
                        print(f"[MATCH] {item.item_name} → {score:.4f}")
                        scored.append((score, item))
                    except Exception as e:
                        print(f"[SKIP] item {item.id}: {e}")
                        continue

            scored.sort(key=lambda x: x[0], reverse=True)

            # Always return top 3 matches
            matched_ids = [str(item.id) for score, item in scored[:3]]
            print(f"[RESULT] matched_ids: {matched_ids}")

        except Exception as e:
            print(f"[ERROR] camera_search: {e}")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    return JsonResponse({"matched_ids": matched_ids})

@login_required
def audio_search(request):
    results = []
    transcript = ""
    if request.method == "POST" and request.FILES.get("query_audio"):
        # Load Whisper
        whisper_model = whisper.load_model("base")

        # Save uploaded audio temporarily
        query_audio = request.FILES["query_audio"]
        temp_path = os.path.join(settings.MEDIA_ROOT, "temp_audio.wav")
        with open(temp_path, "wb+") as f:
            for chunk in query_audio.chunks():
                f.write(chunk)

        # Transcribe audio to text
        result = whisper_model.transcribe(temp_path)
        transcript = result["text"].strip()

        # Search items by transcript keywords
        if transcript:
            keywords = transcript.split()
            query = Q()
            for word in keywords:
                query |= Q(item_name__icontains=word) | Q(description__icontains=word)
            results = list(Item.objects.filter(query).distinct())

        if os.path.exists(temp_path):
            os.remove(temp_path)

    return render(request, "items/audio_search.html", {
        "results": results,
        "transcript": transcript,
    })




# -------------------------------
# FORGOT / RESET PASSWORD
# -------------------------------
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = request.build_absolute_uri(f"/reset-password/{uid}/{token}/")
            send_mail(
                "Password Reset",
                f"Click to reset your password: {reset_link}",
                settings.DEFAULT_FROM_EMAIL,
                [email],
            )
        except User.DoesNotExist:
            pass
        return redirect("forgot_password_done")
    return render(request, "items/forgot_password.html")


def forgot_password_done(request):
    return render(request, "items/forgot_password_done.html")


def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == "POST":
            password = request.POST.get("password")
            user.set_password(password)
            user.save()
            return redirect("reset_password_complete")
        return render(request, "items/reset_password.html")
    return render(request, "items/reset_password_invalid.html")


def reset_password_complete(request):
    return render(request, "items/reset_password_complete.html")
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from .forms import AURegisterForm, ItemForm, ClaimForm
from .models import Item, Claim


# -------------------------------
# REGISTER
# -------------------------------
def register(request):
    if request.method == "POST":
        form = AURegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = AURegisterForm()
    return render(request, "items/register.html", {"form": form})


# -------------------------------
# LOGIN
# -------------------------------
def user_login(request):
    if request.method == "POST":
        email    = request.POST.get("email")
        password = request.POST.get("password")
        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            return render(request, "items/login.html", {"error": "Invalid email or password"})

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            return render(request, "items/login.html", {"error": "Invalid email or password"})

    return render(request, "items/login.html")


# -------------------------------
# HOME
# -------------------------------
@login_required
def home(request):
    items = Item.objects.all().order_by("-date_reported")
    context = {
        "items":           items,
        "total_items":     items.count(),
        "not_collected":      items.filter(status="Not Collected").count(),
        "collected_items": items.filter(status="Collected").count(),  # ✅ replaces found_items
    }
    return render(request, "items/home.html", context)


# -------------------------------
# ADD ITEM
# -------------------------------
@login_required
def add_item(request):
    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item              = form.save(commit=False)
            item.reported_by  = request.user
            item.status       = "Not Collected"
            item.save()
            return redirect("home")
        else:
            print(form.errors)
    else:
        form = ItemForm()
    return render(request, "items/add_item.html", {"form": form})


# -------------------------------
# LOGOUT
# -------------------------------
def user_logout(request):
    logout(request)
    return redirect("login")


# -------------------------------
# UPDATE STATUS
# -------------------------------
@login_required
def update_status(request, item_id):
    item        = get_object_or_404(Item, id=item_id)
    item.status = "Collected" if item.status == "Not Collected" else "Not Collected"
    item.save()
    return redirect("home")


# -------------------------------
# MY ITEMS
# -------------------------------
@login_required
def my_items(request):
    items = Item.objects.filter(reported_by=request.user).order_by("-date_reported")
    return render(request, "items/my_items.html", {"items": items})


# -------------------------------
# ITEM DETAIL
# -------------------------------
@login_required
def item_detail(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    return render(request, "items/item_detail.html", {"item": item})


# -------------------------------
# CLAIM ITEM
# ✅ Only reporter of the item can open this form
# -------------------------------
@login_required
def claim_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    # ✅ Only the reporter can fill the claim form
    if request.user != item.reported_by:
        return render(request, "items/error.html", {
            "message": "Only the person who reported this item can process a claim."
        })

    # ✅ Already collected
    if item.status == "Collected":
        return render(request, "items/error.html", {
            "message": "This item has already been collected."
        })

    if request.method == "POST":
        form = ClaimForm(request.POST, request.FILES)
        if form.is_valid():
            claim           = form.save(commit=False)
            claim.item      = item
            claim.filled_by = request.user
            claim.save()

            # ✅ Auto mark item as Collected
            item.status = "Collected"
            item.save()

            # ✅ Send confirmation email to claimer
            # ✅ Send confirmation email to claimer
        try:
            subject = f"✅ Claim Confirmed – {item.item_name} | AULAF"

            message = f"""Dear {claim.claimer_name},

        Your claim has been successfully processed at AULAF (Ahmedabad University Lost & Found).

        ━━━━━━━━━━━━━━━━━━━━━━━━
        CLAIM DETAILS
        ━━━━━━━━━━━━━━━━━━━━━━━━

        Item Name      : {item.item_name}
        Description    : {item.description or "N/A"}
        Location       : {item.get_submitted_at_display() or "N/A"}
        Submission Type: {item.get_submission_type_display()}
        Date Reported  : {item.date_reported.strftime("%d %b %Y, %I:%M %p")}

        ━━━━━━━━━━━━━━━━━━━━━━━━
        YOUR INFORMATION
        ━━━━━━━━━━━━━━━━━━━━━━━━

        Name           : {claim.claimer_name}
        Enrollment No  : {claim.enrollment_no}
        AU Email       : {claim.au_email}
        Claimed On     : {claim.claimed_at.strftime("%d %b %Y, %I:%M %p")}

        ━━━━━━━━━━━━━━━━━━━━━━━━

        Please carry your AU ID card when collecting the item from the Lost & Found desk.

        If you have any questions, contact the Lost & Found desk directly.

        Regards,
        AULAF – Ahmedabad University Lost and Found
        """

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[claim.au_email],
                fail_silently=False,   # ← change to True in production
            )

        except Exception as e:
            print(f"[AULAF] Email failed: {e}")   # visible in terminal during dev

            return redirect("item_detail", item_id=item.id)
    else:
        form = ClaimForm()

    return render(request, "items/claim_item.html", {"form": form, "item": item})


# -------------------------------
# VIEW CLAIMS
# ✅ Only reporter can see all claims for their item
# -------------------------------
@login_required
def view_claims(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    if request.user != item.reported_by:
        return render(request, "items/error.html", {
            "message": "You are not authorized to view claims for this item."
        })

    claims = Claim.objects.filter(item=item).order_by("-claimed_at")
    return render(request, "items/view_claims.html", {"item": item, "claims": claims})
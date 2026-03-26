from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Item, Notification
from .forms import ItemForm

#import matcher 
from .image_match import find_matches, create_match_notifications


@login_required
def home_view(request):
    notifications = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).order_by('-id')

    return render(request, 'home.html', {
        'notifications': notifications
    })

@login_required
def add_item_view(request):
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)

        if form.is_valid():
            item = form.save(commit=False)
            item.reported_by = request.user
            item.save()

            matches = find_matches(item)

            create_match_notifications(item, matches)

            return redirect('home')

    else:
        form = ItemForm()

    return render(request, 'add_item.html', {'form': form})

@login_required
def all_items_view(request):
    items = Item.objects.all().order_by('-id')

    return render(request, 'all_items.html', {
        'items': items
    })


#view matched with a specific image 
@login_required
def item_matches_view(request, item_id):
    item = Item.objects.get(id=item_id)

    matches = find_matches(item)

    return render(request, 'matches.html', {
        'item': item,
        'matches': matches
    })

#notification as read one 
@login_required
def mark_notifications_read(request):
    Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).update(is_read=True)

    return redirect('home')
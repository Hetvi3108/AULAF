from django.urls import path
from . import views

urlpatterns = [
    path("",                          views.user_login,    name="login"),
    path("register/",                 views.register,      name="register"),
    path("home/",                     views.home,          name="home"),
    path("add/",                      views.add_item,      name="add_item"),
    path("logout/",                   views.user_logout,   name="logout"),
    path("update/<int:item_id>/",     views.update_status, name="update_status"),
    path("my-items/",                 views.my_items,      name="my_items"),
    path("item/<int:item_id>/",       views.item_detail,   name="item_detail"),

    # ✅ NEW claim URLs
    path("claim/<int:item_id>/",      views.claim_item,    name="claim_item"),
    path("claims/<int:item_id>/",     views.view_claims,   name="view_claims"),
]
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
    path("claim/<int:item_id>/",            views.claim_item,    name="claim_item"),
    path("claims/<int:item_id>/",           views.view_claims,   name="view_claims"),
    path("item/<int:item_id>/edit/",        views.edit_item,     name="edit_item"),
    path("item/<int:item_id>/delete/",      views.delete_item,   name="delete_item"),
    path("claim/edit/<int:claim_id>/",      views.edit_claim,    name="edit_claim"),
    path("claim/delete/<int:claim_id>/",    views.delete_claim,  name="delete_claim"),
    path("complaint/<int:item_id>/",      views.submit_complaint,  name="submit_complaint"),
    path("complaint/general/",            views.submit_complaint,  name="submit_complaint_general"),
    path("complaint/success/",            views.complaint_success, name="complaint_success"),
    path("complaints/",                   views.my_complaints,     name="my_complaints"),
    path("complaint/detail/<int:pk>/",    views.complaint_detail_view, name="complaint_detail_view"),
    path("search/image/", views.image_search, name="image_search"),
    path("search/audio/",  views.audio_search,  name="audio_search"),
    path("search/camera/", views.camera_search, name="camera_search"),
    # Forgot Password URLs
    path("forgot-password/",                          views.forgot_password,        name="forgot_password"),
    path("reset-password/<uidb64>/<token>/",          views.reset_password,         name="reset_password"),
    path("forgot-password/done/",                     views.forgot_password_done,   name="forgot_password_done"),
    path("reset-password/complete/",                  views.reset_password_complete, name="reset_password_complete"),
    
]
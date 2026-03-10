from django.urls import path,include
from . import views
from .views import CustomResetPasswordView
from django.contrib.auth import views as auth_views
urlpatterns = [
    # path('', include('django.contrib.auth.urls')),
    path('login/',views.login,name='login'),
    path('register/',views.registration,name='registration'),
    path('activate/<uid64>/<token>/', views.activate_user, name='activate'),
    path('logout/', views.logout, name='logout'),

    path('password_reset/', CustomResetPasswordView.as_view(), name='password-reset'),
    
    # ২. ইমেইল পাঠানো হয়েছে এমন কনফার্মেশন পেজ
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='account/password_reset_done.html'), name='password_reset_done'),
    
    # ৩. ইমেইলের লিঙ্কে ক্লিক করলে যে পেজ আসবে (টোকেন ভেরিফিকেশন)
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='account/password_reset_confirm.html'), name='password_reset_confirm'),
    
    # ৪. পাসওয়ার্ড সফলভাবে রিসেট হওয়ার পেজ
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='account/password_reset_complete.html'), name='password_reset_complete'),

    path('profile/',views.profile_view,name='profile_view'),
    path('users/', views.user_list, name='user_list'),
    path('users/follow/', views.user_follow, name='user_follow'),
    path('users/<username>/', views.user_detail, name='user_detail'),
    
]

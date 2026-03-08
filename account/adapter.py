from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth.models import User

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # যদি ইউজার অলরেডি লগইন থাকে তবে কিছু করার দরকার নেই
        if sociallogin.is_existing:
            return

        # গুগল থেকে আসা ইমেইলটি বের করা
        email = sociallogin.user.email
        if not email:
            return

        # চেক করা এই ইমেইল দিয়ে আগে কোনো ইউজার তৈরি হয়েছে কি না
        try:
            user = User.objects.get(email=email)
            # যদি ইউজার পাওয়া যায়, তবে সোশ্যাল একাউন্টটি ওই ইউজারের সাথে কানেক্ট করে দাও
            sociallogin.connect(request, user)
        except User.DoesNotExist:
            pass
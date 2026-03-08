from django.contrib.auth.models import User
from django.db.models.signals import post_save
from .models import Profile
from django.dispatch import receiver
import requests
from django.core.files.base import ContentFile
from allauth.socialaccount.models import SocialAccount


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()



@receiver(post_save, sender=SocialAccount)
def save_google_avatar(sender, instance, created, **kwargs):
    # যদি নতুন সোশ্যাল অ্যাকাউন্ট তৈরি হয় এবং সেটি গুগল হয়
    if created and instance.provider == 'google':
        avater_url = instance.extra_data.get('picture')
        
        if avater_url:
            # গুগল থেকে ইমেজ ডাটা নিয়ে আসা
            response = requests.get(avater_url)
            if response.status_code == 200:
                # ইউজারের প্রোফাইল খুঁজে বের করা (অথবা তৈরি করা)
                profile, _ = Profile.objects.get_or_create(user=instance.user)
                
                # ইমেজের নাম তৈরি করা (যেমন: user_1_avatar.jpg)
                file_name = f'user_{instance.user.id}_avatar.jpg'
                
                # প্রোফাইল মডেলে ছবি সেভ করা
                profile.avater.save(file_name, ContentFile(response.content), save=True)
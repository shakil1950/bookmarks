# account/context_processors.py ফাইলে এটি লিখলে ভালো (নতুন ফাইল তৈরি করুন)
from .models import Action
from django.db.models import Q

def notifications(request):
    if request.user.is_authenticated:
        # ১. আপনি যাদের ফলো করেন তাদের কাজ
        following_ids = request.user.following.values_list('id', flat=True)
        
        # ২. আপনাকে কেন্দ্র করে অন্যদের কাজ (যেমন: কেউ আপনাকে ফলো করলে)
        # ৩. নিজের কাজগুলো বাদ দিয়ে সব প্রাসঙ্গিক অ্যাকশন ফিল্টার করা
        user_notifications = Action.objects.exclude(user=request.user).filter(
            Q(user__id__in=following_ids) | Q(target_id=request.user.id)
        ).select_related('user', 'user__profile').distinct()[:10]
        
        return {
            'unread_notifications': user_notifications
        }
    return {
        'unread_notifications': []
    }
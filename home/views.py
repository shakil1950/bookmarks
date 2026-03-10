from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from images.models import Image
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.db.models import Count
from account.models import Action
# Create your views here.


def home(request):
    images_list = Image.objects.annotate(
        total_comments=Count('comments') # 'comments' হলো আপনার Comment মডেলের related_name
    ).order_by('-created_at')# নতুন ছবি আগে দেখাবে
    
    # পেজিনেশন: প্রতি পেজে ৮টি করে ছবি
    paginator = Paginator(images_list, 8) 
    page = request.GET.get('page')
    images_only = request.GET.get('images_only')

    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        images = paginator.page(1)
    except EmptyPage:
        if images_only:
            return HttpResponse('') # AJAX এর জন্য খালি রেসপন্স
        images = paginator.page(paginator.num_pages)

    if images_only:
        # শুধুমাত্র ইমেজের অংশটুকু রিটার্ন করবে
        return render(request, 'image/list_images_ajax.html', {'images': images})
    
    context = {
        'images': images,
        'view_source': 'feed'
    }
    return render(request, 'home.html', context)
@login_required
def dashboard(request):
    # ১. আপনার নিজের আপলোড করা ছবিগুলো
    images = Image.objects.filter(user=request.user)
    
    # ২. অ্যাকশন ফিড লজিক:
    actions = Action.objects.exclude(user=request.user)
    following_ids = request.user.following.values_list('id', flat=True)
    
    if following_ids:
        actions = actions.filter(user_id__in=following_ids)
    
    # অপ্টিমাইজেশন
    actions = actions.select_related('user', 'user__profile').prefetch_related('target')

    # ৩. প্যাগিনেশন সেটআপ (প্রতিবারে ১০টি করে অ্যাকশন দেখাবে)
    paginator = Paginator(actions, 10)
    page = request.GET.get('page')
    
    try:
        actions = paginator.page(page)
    except PageNotAnInteger:
        # যদি পেজ নাম্বার না থাকে, তবে প্রথম পেজ দেখাবে
        actions = paginator.page(1)
    except EmptyPage:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # যদি স্ক্রল করতে করতে শেষে চলে আসে এবং AJAX রিকোয়েস্ট হয়, তবে খালি রেসপন্স পাঠাবে
            return HttpResponse('')
        # সাধারণ রিকোয়েস্টে শেষ পেজ দেখাবে
        actions = paginator.page(paginator.num_pages)

    # ৪. AJAX রিকোয়েস্ট হ্যান্ডেল করা (ইনফিনিট স্ক্রলের জন্য)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'actions/action/list.html', {'actions': actions})

    context = {
        'section': 'dashboard',
        'images': images,
        'actions': actions,
    }
    return render(request, 'dashboard.html', context)
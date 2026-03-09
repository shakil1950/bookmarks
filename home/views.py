from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from images.models import Image
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.db.models import Count
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
    images=Image.objects.filter(user=request.user)
    print(images)
    context={
        'images':images
    }
    return render(request, 'dashboard.html',context)

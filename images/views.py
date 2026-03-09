import requests
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .forms import ImageCreateForm
from django.core.files.base import ContentFile
from django.utils.text import slugify
from .models import Image,Comment
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@login_required
def image_create(request):
    if request.method == 'POST':
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            new_image = form.save(commit=False)
            
            # ১. আগে ইউজার সেট করুন (যাতে ডাটাবেস এরর না দেয়)
            new_image.user = request.user
            
            # ২. ইমেজ ডাউনলোড লজিক
            image_url = cd['url']
            name = slugify(new_image.title)
            extension = image_url.rsplit('.', 1)[1].lower()
            image_name = f'{name}.{extension}'
            
            response = requests.get(image_url)
            # ৩. ইমেজটি ফাইলে সেভ করুন (save=False মানে এখনো ডাটাবেসে যাবে না)
            new_image.image.save(image_name, ContentFile(response.content), save=False)
            
            # ৪. এবার ফাইনালি সব ডাটা একসাথে সেভ করুন
            new_image.save()
            
            messages.success(request, 'Image added successfully')
            return redirect('dashboard') # বা আপনার ইচ্ছেমতো পেজ
    else:
        form = ImageCreateForm(data=request.GET)
    
    return render(request, 'image/create.html', {'form': form})


@login_required
def list_image(request):
    images=Image.objects.filter(user=request.user)
    context={
        'images':images
    }
    
    return render(request,'image/list.html',context)


def image_detail(request, id, slug):
   
    image = get_object_or_404(Image, id=id, slug=slug)
    back_url = request.META.get('HTTP_REFERER')
    
    # যদি আগের কোনো লিঙ্ক না থাকে, তবে ডিফল্ট হিসেবে হোম পেজে পাঠাবে
    if not back_url:
        back_url = '/'
    return render(request, 'image/detail.html', {
        'section': 'images',
        'image': image,
        'back_url':back_url
    })

@login_required
@require_POST
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like':
                image.users_like.add(request.user)
            else:
                image.users_like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except Image.DoesNotExist:
            pass
    return JsonResponse({'status': 'error'})

@login_required
@require_POST
def image_comment(request):
    image_id = request.POST.get('id')
    body = request.POST.get('body')
    if image_id and body:
        try:
            image = Image.objects.get(id=image_id)
            comment = Comment.objects.create(image=image, user=request.user, body=body)
            return JsonResponse({
                'status': 'ok',
                'user': request.user.username,
                'body': comment.body,
                'created': 'Just now'
            })
        except Image.DoesNotExist:
            return JsonResponse({'status': 'error'})
    return JsonResponse({'status': 'error'})
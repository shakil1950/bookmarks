import requests
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .forms import ImageCreateForm,ImageUploadForm
from django.core.files.base import ContentFile
from django.utils.text import slugify
from .models import Image,Comment
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from account.utils import create_action
import redis
from django.db import transaction
from django.conf import settings


@login_required
def image_create(request):
    if request.method == 'POST':
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            new_image = form.save(commit=False)
            new_image.user = request.user
            new_image.upload_type = 'bookmark'
            image_url = cd['url']
            name = slugify(new_image.title)
            extension = image_url.rsplit('.', 1)[1].lower()
            image_name = f'{name}.{extension}'
            response = requests.get(image_url)
            new_image.image.save(image_name, ContentFile(response.content), save=False)
            new_image.save()
            new_image = form.save()
            create_action(request.user, 'bookmarked image', new_image)
            messages.success(request, 'Image added successfully')
            return redirect('explore') 
    else:
        form = ImageCreateForm(data=request.GET)
    
    return render(request, 'image/create.html', {'form': form})


@login_required
def image_upload(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            new_image = form.save(commit=False)
            new_image.user = request.user
            new_image.upload_type = 'manual' 
            new_image.save()
            return redirect('explore') 
    return redirect('explore')

@login_required
def list_image(request):
    images=Image.objects.filter(user=request.user)
    context={
        'images':images
    }
    
    return render(request,'image/list.html',context)



r = redis.Redis(host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB)



def image_detail(request, id, slug):
   
    image = get_object_or_404(Image, id=id, slug=slug)
    back_url = request.META.get('HTTP_REFERER')
  
    total_views = r.incr(f'image:{image.id}:views')
    r.zincrby('image_ranking', 1, image.id)
   
    if not back_url:
        back_url = '/'
    return render(request, 'image/detail.html', {
        'section': 'images',
        'image': image,
        'back_url':back_url,
        'total_views': total_views
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


@login_required
def image_ranking(request):
 
    image_ranking = r.zrevrange('image_ranking', 0, -1, withscores=True)[:100]
    
    image_ranking_ids = [int(id) for id, score in image_ranking]
    
   
    most_viewed = list(Image.objects.filter(id__in=image_ranking_ids))

    most_viewed.sort(key=lambda x: image_ranking_ids.index(x.id))
    
    return render(request, 'image/ranking.html', {
        'section': 'ranking',
        'most_viewed': most_viewed
    })


@login_required
def delete_bookmark_image(request, id):
    image = get_object_or_404(Image, id=id)
    
   
    if image.user == request.user or request.user.is_superuser:
        
        
        r.delete(f'image:{image.id}:views')
        r.zrem('image_ranking', image.id)
        
   
        image.delete()
        
      
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.method == 'POST':
            return JsonResponse({'status': 'ok', 'message': 'Deleted successfully'})

      
        messages.success(request, 'Image deleted successfully!')
        return redirect(request.META.get('HTTP_REFERER', 'home'))
        
    else:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
            
        messages.error(request, 'You are not authorized to delete this image.')
        return redirect(request.META.get('HTTP_REFERER', 'home'))



@login_required
def edit_image(request, id):
    if request.method == 'POST':
        # ১. অবজেক্ট খুঁজে বের করা
        image = get_object_or_404(Image, id=id)
        
        # ২. পারমিশন চেক (নিশ্চিত করুন ইউজার লগইন করা আছে)
        if image.user != request.user and not request.user.is_superuser:
            return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
            
        # ৩. ডাটা রিসিভ করা (strip() ব্যবহার করা ভালো)
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        
        print(f'>>> Attempting Save: ID={id}, Title={title}')

        if title:
            try:
                # ৪. অ্যাটমিক ট্রানজ্যাকশন ব্যবহার করা সেভ নিশ্চিত করতে
                with transaction.atomic():
                    image.title = title
                    image.description = description if description else None
                    image.save()
                
                # ৫. কনফার্মেশনের জন্য আবার ডাটাবেস থেকে রিড করা
                image.refresh_from_db()
                print(f'>>> Saved Successfully: {image.title}')

                return JsonResponse({
                    'status': 'ok', 
                    'new_title': image.title, 
                    'new_description': image.description or ''
                })
            except Exception as e:
                print(f'>>> Save Error: {str(e)}')
                return JsonResponse({'status': 'error', 'message': 'Database error'}, status=500)
        
        return JsonResponse({'status': 'error', 'message': 'Title is required'}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
    
    

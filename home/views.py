from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from images.models import Image
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.db.models import Count
from account.models import Action
from django.http import JsonResponse
import redis
from django.conf import settings
# Create your views here.
r = redis.Redis(host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB)

def home(request):
    images_list = Image.objects.annotate(
        total_comments=Count('comments') 
    ).order_by('-created_at')
    trending_ids = r.zrevrange('image_ranking', 0, 10)
    trending_ids = [int(id) for id in trending_ids]
    
  
    
    trending_images = list(Image.objects.filter(id__in=trending_ids))
    trending_images.sort(key=lambda x: trending_ids.index(x.id))
   
    paginator = Paginator(images_list, 8) 
    page = request.GET.get('page')
    images_only = request.GET.get('images_only')

    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        images = paginator.page(1)
    except EmptyPage:
        if images_only:
            return HttpResponse('') 
        images = paginator.page(paginator.num_pages)

    if images_only:
       
        return render(request, 'image/list_images_ajax.html', {'images': images})
    
    context = {
        'images': images,
        'view_source': 'feed',
        'trending_images':trending_images,
        
    }
    return render(request, 'home.html', context)


@login_required
def dashboard(request):
    
    user_images = Image.objects.filter(user=request.user)
    
    
    following_ids = request.user.following.values_list('id', flat=True)
    images_feed_list = Image.objects.filter(user_id__in=following_ids)\
                                   .select_related('user')\
                                   .order_by('-created_at')

   
    paginator = Paginator(images_feed_list, 8)
    page = request.GET.get('page')
    
    try:
        images_feed = paginator.page(page)
    except PageNotAnInteger:
        images_feed = paginator.page(1)
    except EmptyPage:
        if request.GET.get('ajax'):
            return JsonResponse({'images': [], 'has_next': False})
        images_feed = paginator.page(paginator.num_pages)

  
    if request.GET.get('ajax'):
        image_data = []
        for img in images_feed:
            
            try:
              
                
                if hasattr(img.user, 'profile') and img.user.profile.avater:
                    avatar_url = img.user.profile.avater.url
                else:
                    avatar_url = f"https://ui-avatars.com/api/?name={img.user.username}"
            except:
                avatar_url = f"https://ui-avatars.com/api/?name={img.user.username}"

            image_data.append({
                'id': img.id,
                'title': img.title,
                'image': img.image.url,
                'url': img.get_absolute_url(),
                'user': img.user.username,
                'user_avatar': avatar_url,
                'user_url': img.user.get_absolute_url(),
                'created': img.created_at.strftime("%d %b"),
                'can_delete': (img.user == request.user or request.user.is_superuser),
            })
        return JsonResponse({
            'images': image_data,
            'has_next': images_feed.has_next()
        })

    return render(request, 'dashboard.html', {
        'section': 'dashboard',
        'images': user_images,
        'images_feed': images_feed,
    })
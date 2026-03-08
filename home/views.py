from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from images.models import Image
# Create your views here.


def home(request):
    images=Image.objects.all()
    context={
        'images':images,
        'view_source': 'feed'
    }
    return render(request,'home.html',context)

@login_required
def dashboard(request):
    images=Image.objects.filter(user=request.user)
    print(images)
    context={
        'images':images
    }
    return render(request, 'dashboard.html',context)

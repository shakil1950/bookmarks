from django.shortcuts import render,redirect,get_list_or_404
from .forms import RegistrationForm,ChangePaswordForm
from django.contrib import messages
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login,authenticate,logout as auth_logout
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes,force_str
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm,ProfileUpdateForm
from images.models import Image
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Contact,Action
from django.db.models import Count
from django.db.models import Q
from django.contrib.auth.hashers import check_password
from django.contrib.auth import update_session_auth_hash
from account.utils import create_action
from django.core.paginator import Paginator

def login(request):

    if request.method == 'POST':
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username_or_email, password=password)
        
        if user is not None:
            if user.is_active:
                auth_login(request, user)
                messages.success(request, f'Welcome {user.username}!')
                return redirect('home')
            else:
                messages.error(request, 'Your account is activate.Please check mail')
        else:
            messages.error(request, 'Invlid user name or password')
            
    return render(request, 'account/login.html')
@login_required
def logout(request):
    auth_logout(request)
    messages.success(request,'Logout successfull')
    return redirect('login')

def registration(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data['password'])
            new_user.is_active = False 
            new_user.save()
            
            try:
                token = default_token_generator.make_token(new_user)
                uid = urlsafe_base64_encode(force_bytes(new_user.pk))
                domain = get_current_site(request).domain
                
    
                relative_url = reverse('activate', kwargs={'uid64': uid, 'token': token})
                activation_link = f"http://{domain}{relative_url}"
                
                message_body = f'হ্যালো {new_user.first_name},\n Please this link to activate id :\n{activation_link}'
                
                send_mail(
                    'Account Activation - Bookmarks',
                    message_body,
                    'shakilahmed.pbl@gmail.com',
                    [new_user.email],
                    fail_silently=False,
                )
                messages.success(request, 'Please check your mail to activate your account!')
                return redirect('login')
            
            except Exception as e:
               
                new_user.delete() 
                messages.error(request, 'Failed to send activation mail. Please check your internet or email.')
               
        else:
            
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegistrationForm()
    
    return render(request, 'account/register.html', {'form': form})

def activate_user(request,uid64,token):
    try:
        uid=force_str(urlsafe_base64_decode(uid64))
        user=User.objects.get(id=uid)
    except(TypeError,ValueError,OverflowError,User.DoesNotExist):
        user=None
    if user is not None and default_token_generator.check_token(user,token):

        user.is_active=True
        user.save()
        messages.success(request,'Account activated')
        return redirect('login')

class CustomResetPasswordView(PasswordResetView):
    template_name = 'account/reset-password-form.html'
    success_url = reverse_lazy('password_reset_done')
    email_template_name = 'account/password_reset_email.html'
    html_email_template_name = 'account/password_reset_email.html'
    
    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        try:
            user = User.objects.get(username=username)
            if user.socialaccount_set.exists():
                messages.info(request, "You are using a social account (Google). Please login directly via Google.")
                return render(request, self.template_name)
            if user.email:
                data = request.POST.copy()
                data['email'] = user.email
                request.POST = data
                return super().post(request, *args, **kwargs)
            else:
                messages.error(request, "No email for this user!")
        except User.DoesNotExist:
            messages.error(request, "Invalid username!")
        
        return render(request, self.template_name)


@login_required
def profile_view(request):
    
    if request.method=='POST':
        u_form=UserUpdateForm(request.POST,instance=request.user)
        p_form=ProfileUpdateForm(request.POST,request.FILES,instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request,'Updated')
            return redirect('profile_view')
        else:
            messages.error(request,'Problem on updating information')
            return redirect('profile_view')
    else:

        u_form=UserUpdateForm(instance=request.user)
        p_form=ProfileUpdateForm(instance=request.user.profile)

    context={
        'u_form':u_form,
        'p_form':p_form
    }
    return render(request,'account/profile.html',context)
@login_required
def profile_update(request):

    if request.method=='POST':
        u_form=UserUpdateForm(request.POST,instance=request.user)
        p_form=ProfileUpdateForm(request.POST,request.FILES,instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request,'Updated')
            return redirect('profile')
        else:
            messages.error(request,'Problem on updating information')
            return redirect('profile')
    else:

        u_form=UserUpdateForm(instance=request.user)
        p_form=ProfileUpdateForm(instance=request.user.profile)

    context={
        'u_form':u_form,
        'p_form':p_form
    }

    return render(request,'account/profile.html',context)


@login_required
def user_list(request):
    users = User.objects.filter(is_active=True)
    top_creators = User.objects.annotate(
        total_images=Count('image_create')
    ).order_by('-total_images')[:4]
    return render(request, 'account/user/user_list.html', 
                  {'section': 'people', 'users': users,'top_creators': top_creators})

@login_required
def user_detail(request, username):
    user = get_object_or_404(User, username=username, is_active=True)
    return render(request, 'account/user/user_detail.html', 
                  {'section': 'people', 'user': user,})

@login_required
@require_POST
def user_follow(request):
    user_id = request.POST.get('id')
    action = request.POST.get('action')
    
    if user_id and action:
        try:
            user = User.objects.get(id=user_id)
            
            if action == 'follow':
                Contact.objects.get_or_create(user_from=request.user, user_to=user)
                
                create_action(request.user, 'is following', user)
            else:
                Contact.objects.filter(user_from=request.user, user_to=user).delete()
                
                create_action(request.user, 'stopped following', user)
            
            return JsonResponse({'status': 'ok'})
            
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'})
            
    return JsonResponse({'status': 'error', 'message': 'Invalid data'})
@login_required
def notification_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({'notifications': []})
    actions = Action.objects.exclude(user=request.user).filter(
        Q(target_id=request.user.id) | Q(user__id__in=request.user.following.values_list('id', flat=True))
    ).select_related('user').order_by('-created')[:10]

    data = []
    for act in actions:
        data.append({
            'id': act.id,
            'user': act.user.username,
            'verb': act.verb,
            'created': act.created.strftime('%b %d, %H:%M')
        })
    return JsonResponse({'notifications': data})

@login_required
def activity_list(request):
    actions = Action.objects.all().select_related('user', 'user__profile')
    paginator = Paginator(actions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.GET.get('ajax'):
        activity_data = []
        for act in page_obj:
            activity_data.append({
                'id': act.id,
                'user': act.user.username,
                'user_avatar': act.user.profile.avater.url if act.user.profile.avater else f"https://ui-avatars.com/api/?name={act.user.username}",
                'verb': act.verb,
                'created': act.created.strftime("%b %d, %H:%M")
            })
        return JsonResponse({
            'activities': activity_data,
            'has_next': page_obj.has_next()
        })
    
    return render(request, 'account/activity_list.html', {'page_obj': page_obj})

@login_required
def change_password(request):
    form=ChangePaswordForm()
    if request.method=="POST":
        form=ChangePaswordForm(request.POST)
        if form.is_valid():
            pass1=form.cleaned_data['pass1']
            prev_pass=form.cleaned_data['prev_pass']
            if not check_password(prev_pass,request.user.password):
                messages.error(request,'Wrong current password')
                return redirect('change-password')
            else:
                request.user.set_password(pass1)
                request.user.save()
                update_session_auth_hash(request,request.user)
                messages.success(request,'password change successfully')
                return redirect('profile_view')
    else:
        form=ChangePaswordForm()
    context={
        'form':form
    }
    return render(request,'account/change-password.html',context)
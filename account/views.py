from django.shortcuts import render,redirect,get_list_or_404
from .forms import RegistrationForm
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
def changepassword(request):
    pass

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
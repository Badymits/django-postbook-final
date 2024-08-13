from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import Account
from home.models import Post, Comment, SavedPostsModel, LikeModel, DislikeModel
from .forms import RegisterModelForm, LoginModelForm, EditProfileForm

# Create your views here.
def loginView(request):
    form = LoginModelForm()
    
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        email=request.POST['email']
        password = request.POST['password']
        try: 
            user = get_object_or_404(Account, email=email)
            print(user.username)
        except:
            messages.error(request, 'Account does not exist', extra_tags='login')
        try:
            # THIS IS VERY MISLEADING POTANGINAAAAAAAAAAAAAAAAAAAAAAAAAA
            # since the username field is set to email, USE THAT INSTEAD TO PASS IN THE USERNAME PARAM
            user = authenticate(username=email, password=password)
            login(request, user)
            return redirect('home')
        except:
            messages.error(request, 'Credential Error', extra_tags='login')
            return redirect('login')
        
    context = {'login_form': form}
    
    return render(request, 'accounts/login.html', context)

def registerView(request):
    
    form = RegisterModelForm()
    context = {'reg_form': form}
   
    if request.method == 'POST':
        # add password authentication
        form = RegisterModelForm(request.POST)
        
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        password1 = request.POST['password1']
        
        try:
            email_user = get_object_or_404(Account, email=email)
        except:
            email_user = None
            
        try:
            username = get_object_or_404(Account, username=username)
        except:
            username = None
            
        if email_user is not None:
            context['message'] = 'Email already exists'
            messages.error(request, 'Email already exists', extra_tags='register')
            return render(request, 'accounts/register.html', context)
        
        if username is not None:
            messages.error(request, 'Username is already taken', extra_tags='register')
            return render(request, 'accounts/register.html', context)
        
        if password != password1:
            messages.error(request, "Passwords don't match", extra_tags='register')
            return render(request, 'accounts/register.html', context)
        
        if form.is_valid():
            form.save()
            
            messages.success(request, 'Register Successfull! You may enter your credentials', extra_tags='login')
            return redirect('login')

    return render(request, 'accounts/register.html', context)

def logoutView(request):
    
    logout(request)
    
    return redirect('login')


@login_required(login_url='login')
def userView(request, id, tab):
    
    context = {}
    
    try:
        user = get_object_or_404(Account, id=id)
        context['user'] = user
        
        if tab == 'posts':
            user_posts = Post.objects.filter(user=user).order_by('-date_posted')
            context['user_posts'] = user_posts
            
        elif tab == 'comments':
            user_comments = Comment.objects.filter(user=user).order_by('-date_posted')
            context['user_comments'] = user_comments
        
        elif tab == 'saved':
            user_saved_posts = SavedPostsModel.objects.filter(users__id=user.id)
            context['user_saved_posts'] = user_saved_posts
        
        elif tab == 'upvoted':
            upvotes = LikeModel.objects.filter(users__id=user.id)
            context['upvotes'] = upvotes
            
        elif tab == 'downvoted':
            downvotes = DislikeModel.objects.filter(users__id=user.id)
            context['downvotes'] = downvotes
        
        return render(request, 'accounts/profile_page.html', context)
    except:
        context['message'] = 'Account does not exist'
        context['posts'] = Post.objects.all()
        return render(request, 'home/home.html',context)

@login_required(login_url='login')
def editProfile(request, id):
    
    context = {}
    form = EditProfileForm()
    try:
        user = get_object_or_404(Account, id=id)
        
    except:
        context['message'] = 'User does not exist'
        return redirect('home')
    
    if request.method == 'POST':
        print('post data: ',request.POST)
        form = EditProfileForm(request.POST, request.FILES, instance=user)
        
        if form.is_valid():
            profile = form.save(commit=False)
            
            if form.cleaned_data['bio']:
                profile.bio = form.cleaned_data['bio']
            
            if form.cleaned_data['profile_pic']:
                profile.profile_pic = form.cleaned_data['profile_pic']

            if form.cleaned_data['banner_pic']:
                profile.banner_pic = form.cleaned_data['banner_pic']
                
            profile.save()
            messages.success(request, 'Changes Saved', extra_tags='settings')
            return redirect('settings', 'profile')
        
    return JsonResponse(context)
    
    
    
@login_required(login_url='login')
def settingsView(request, tab):
    
    context = {}
    
    
    return render(request, 'accounts/settings.html', context)
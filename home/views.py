from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core import serializers
from datetime import datetime
import jsonpickle
from accounts.models import Account
from .models import Post, Comment, LikeModel, DislikeModel, SavedPostsModel, Notification
from .forms import CreatePostForm, UpdatePostForm, CreateCommentForm, EditCommentForm
from django.db.models import Q

HOME_LEVEL = 80

# Create your views here.


# all funcs will be camel cases
@login_required(login_url='login')
def homePage(request):
    
    posts = Post.all_objects.all().order_by('-date_posted')
    notifications = Notification.objects.filter(receiver=request.user).order_by('-date_added')
    context = {'user': request.user, 'posts': posts, 'notifications': notifications}
    return render(request, 'home/home.html', context)

@login_required(login_url='login')
def createPost(request):
    
    context = {}
    form = CreatePostForm()
    req_user = Account.objects.get(email=request.user.email)
    
    if request.method == 'POST':
        form = CreatePostForm(request.POST, request.FILES)
        
        if form.is_valid():
            post = form.save(commit=False)
            
            post.user = req_user
            form.save()
            
            messages.success(request, 'POST CREATED!', extra_tags='home')
            context['message'] = 'Post created!'
            return redirect('home')
        else:
            print('ERROR')
            messages.error(request, 'Something went wrong...', extra_tags='home')
            
    context = {'form': form}
    
    return render(request, 'home/create_post.html', context)

@login_required(login_url='login')
def detailPost(request, id):
    
    try:
        post = get_object_or_404(Post, id=id)
 
    except:
        print('ERROR')
        messages.error(request, 'Post does not exist')
        return redirect('home')
    context = {'post': post}
    try:
        comments = Comment.all_objects.filter(main_post=post.id, comment_level=1).order_by('-date_posted')
        context['comments'] = comments
    except:
        context['message'] = 'No comments'  
    
    return render(request, 'home/detail_post.html', context)


@login_required(login_url='login')
def editPost(request, id):
    
    context = {}
    
    try:
        post = get_object_or_404(Post, id=id)
        form = UpdatePostForm(instance=post)
    except:
        messages.error(request, 'Post does not exist')
        return redirect('home')
    
    if request.method == 'POST':
        
        form = UpdatePostForm(request.POST or None, request.FILES or None, instance=post)
        
        if form.is_valid():
            post = form.save(commit=False)
            
            # cleaned data meaning the new data that has been sent thru POST request 
            # and can only be accessed once is_valid has been called
            post.title = form.cleaned_data['title']
            post.body = form.cleaned_data['body']
            
            # check if image has been passed thru
            if form.cleaned_data['image']:
                post.image = form.cleaned_data['image']
            post.save()
            
            messages.success(request, 'Edit Successful!', extra_tags='detail')
            
            return redirect('detail-post', id)
        else:
            messages.error(request, 'Something went wrong...', extra_tags='detail')
    
    # setting the initial values to be rendered in the form
    form = UpdatePostForm(
        initial={
            'user': post.user,
            'title': post.title,
            'body': post.body,
            'image': post.image
        }
    )
    context['post'] = post
    context['form'] = form
    
    
    return render(request, 'home/edit_post.html', context)


@login_required(login_url='login')
def deletePost(request, id):
    context = {}
    try:
        post = get_object_or_404(Post, id=id)
        post.delete()
        
        context['message'] = 'Post has been deleted!'
        messages.info(request, 'Post has been deleted', extra_tags='home') 
        return redirect('home')
        
    except:
        context['message'] = 'post not found'
        return JsonResponse(context)
    
@login_required(login_url='login')
def savePost(request, id):
    
    context = {}
    
    try:
        post = get_object_or_404(Post, id=id)
    except:
        context['message'] = 'Post does not exist'
        
        return JsonResponse(context)
    
    try:
        saved_post = get_object_or_404(SavedPostsModel, post__id=id)
        
    except:
        
        saved_post = SavedPostsModel.objects.create(
            post=post
        )
        print('user added')
        saved_post.users.add(request.user)
        context['message'] = 'Post saved'
        context['action_taken'] = 'Added'
    
        return JsonResponse(context)
    
    if saved_post.users.filter(id=request.user.id).exists():
        print('USER REMOVEDDD')
        saved_post.users.remove(request.user)
        context['message'] = 'Removed from saved'
        context['action_taken'] = 'Removed'
    else:
        print('USER ADDED!!')
        saved_post.users.add(request.user)
        context['message'] = 'Post saved'
        context['action_taken'] = 'Added'
    
    return JsonResponse(context)
    
@login_required(login_url='login')
def updateVotePost(request, id):
    
    context = {}
    
    try:
        post = get_object_or_404(Post, id=id)

    except:
        
        context['message'] = 'Post does not exist'
        return JsonResponse(context)
    
    
    if request.GET.get('option') == 'like':
        
        # get the like and dislike objs to check if user exists in any of the two models
        try:
            like_obj = get_object_or_404(LikeModel, post=post)
        except:
            like_obj = LikeModel.objects.create(
                post=post,
            )
        context['message'] = 'Liked Post!'
        
        try:
            dislike_obj = get_object_or_404(DislikeModel, post=post)
        except:
            dislike_obj = None
        
        # if user clicks on an already liked post
        if like_obj.users.filter(id=request.user.id).exists():
            like_obj.users.remove(request.user)
            
            context['option'] = 'removed like'
            
        # first time/ clicking on a post that has no like vote
        else:
            if dislike_obj is not None:
                dislike_obj.users.remove(request.user)
                context['dislike_count'] = dislike_obj.users.all().count()
            else:
                context['dislike_count'] = 0
            like_obj.users.add(request.user)
            
        # returning the user count for like and dislike model to render immediately
            context['option'] = 'added'
        context['like_count'] = like_obj.users.all().count()
        
    # same process with like, getting the like and dislike object. Then remove/add user depending on the action/option
    elif request.GET.get('option') == 'dislike':
        print(request.GET.get('option'))
        try:
            like_obj = get_object_or_404(LikeModel, post=post)
        except:
            like_obj = None
        
        try:
            dislike_obj = get_object_or_404(DislikeModel, post=post)
        except:
            dislike_obj = DislikeModel.objects.create(
                post=post
            )
        context['message'] = 'Disliked Post!'
        
        if dislike_obj.users.filter(id=request.user.id).exists():
            dislike_obj.users.remove(request.user)
            context['option'] = 'removed dislike'
            
        else:
            if like_obj is not None:
                like_obj.users.remove(request.user)
                context['like_count'] = like_obj.users.all().count()
            else:
                context['like_count'] = 0
            dislike_obj.users.add(request.user)
            
            context['option'] = 'added'
        
        context['dislike_count'] = dislike_obj.users.all().count()
    
    return JsonResponse(context)



@login_required(login_url='login')
def createComment(request, id):
    
    form = CreateCommentForm()
    context = {}
    try:
        main_post = get_object_or_404(Post, id=id)
        print(main_post.id)
    except:
        messages.error(request, 'Post does not exist')
    
    if request.method == 'POST':
        form = CreateCommentForm(request.POST or None, request.FILES or None)
        
        if form.is_valid():
            print(request.POST)
            comment = form.save(commit=False)
            
            comment.main_post = main_post
            comment.user = request.user
            comment.is_edited = False
            
            if request.POST['is_reply'] == 'true':
                # put in request data the main comment for this line pota
                try:
                    main_comment = get_object_or_404(Comment, id=request.POST['main_comment_id'])
                    comment.reply = main_comment
                    if comment.comment_level is None:
                        comment.comment_level = main_comment.comment_level + 1
                        
                except:
                    messages.error(request, 'Comment does not exist or has been deleted', extra_tags='detail')
                    return redirect('detail-post', id)
            else:
                
                comment.comment_level = 1
            
            comment.save()
            context['server_message'] = 'Comment Made!'           
            
            # we can just pass in the variables thru context like the server_message one. 
            # Too lazy but same result . Then pass the context var all together
            return JsonResponse({
                'comment': jsonpickle.encode(comment),
                'comment_id': comment.id,
                'comment_user': comment.user.username,
                'comment_body': comment.body,
                'comment_date': comment.date_posted,
                'comment_level': comment.comment_level,
                'has_profile_pic': True if comment.user.profile_pic else False,
                'img_path': f'http://127.0.0.1:8000{comment.user.profile_pic.url}' if comment.user.profile_pic else "http://127.0.0.1:8000/static/images/profile/images/xianyun.jpg", # refer to default if empty
                'server_message': 'Comment Made!',
            })
        else:
            messages.error(request, 'There was an error', extra_tags='detail')
            
    
    
    return JsonResponse(context)

@login_required(login_url='login')
def editComment(request, id):
    
    context = {}
    
    try:
        comment = get_object_or_404(Comment, id=id)
    except:
        context['message'] = 'Comment has been deleted'
        messages.error(request, 'Comment has been deleted', extra_tags='detail')
        
    if request.method == 'POST':
       
        form = EditCommentForm(request.POST or None, instance=comment)
        
        if form.is_valid():
            
            comment = form.save(commit=False)
            comment.body = form.cleaned_data['body']
            
            comment.save()
            
            context['server_message'] = 'Edit Saved!'
            context['comment'] = comment.body
            return JsonResponse(context)
        
    context['message'] = 'lods may comment lods'
    context['comment'] = comment.body
    
    return JsonResponse(context)

@login_required(login_url='login')
def deleteComment(request, id):
    
    context = {}
    try:
        comment = get_object_or_404(Comment, id=id)
        
        comment.soft_delete()
        context['server_message'] = 'Comment Deleted'
        return JsonResponse(context)
    except:
        context['server_message'] = 'Comment does not exist'
        return JsonResponse(context)

# removes the comment completely
@login_required(login_url='login')
def removeComment(id):
    
    context = {}
    try:
        comment = get_object_or_404(Comment, id=id)
        comment.delete()
        context['server_message'] = 'Comment Deleted from DB'
        return JsonResponse(context)
        
    except:
        context['server_message'] = 'Comment does not exist'
        return JsonResponse(context)
    
@login_required(login_url='login')
def updateVoteComment(request, id):
    
    context = {}
    
    try:
        comment = get_object_or_404(Comment, id=id)
    except:
        context['message'] = 'No comment exists'
        return JsonResponse(context)
    
    if request.GET.get('option') == 'like':
        
        try:
            like_obj = get_object_or_404(LikeModel, comment=comment)
        except:
            like_obj = LikeModel.objects.create(
                comment=comment,
            )
        context['message'] = 'Liked Post!'
        
        try:
            dislike_obj = get_object_or_404(DislikeModel, comment=comment)
        except:
            dislike_obj = None
        
        
        if like_obj.users.filter(id=request.user.id).exists():
            like_obj.users.remove(request.user)
            
            context['option'] = 'removed like'
        else:
            if dislike_obj is not None:
                dislike_obj.users.remove(request.user)
                context['dislike_count'] = dislike_obj.users.all().count()
            else:
                context['dislike_count'] = 0
            like_obj.users.add(request.user)
            
            
            context['option'] = 'added'
        context['like_count'] = like_obj.users.all().count()
        
        return JsonResponse(context)
        
            
    elif request.GET.get('option') == 'dislike':
        print(request.GET.get('option'))
        try:
            like_obj = get_object_or_404(LikeModel, comment=comment)
        except:
            like_obj = None
        
        try:
            dislike_obj = get_object_or_404(DislikeModel, comment=comment)
        except:
            dislike_obj = DislikeModel.objects.create(
                comment=comment
            )
        context['message'] = 'Disliked Post!'
        
        if dislike_obj.users.filter(id=request.user.id).exists():
            dislike_obj.users.remove(request.user)
            context['option'] = 'removed dislike'
            
        else:
            if like_obj is not None:
                like_obj.users.remove(request.user)
                context['like_count'] = like_obj.users.all().count()
            else:
                context['like_count'] = 0
            dislike_obj.users.add(request.user)
            
            context['option'] = 'added'
        
        context['dislike_count'] = dislike_obj.users.all().count()
    
        return JsonResponse(context)

@login_required(login_url='login')
def getSearchResults(request):
    
    context = {}
    
    keyword = request.GET.get('search')
    results = Post.objects.filter(
        Q(title__icontains=keyword) |
        Q(user__username__icontains=keyword)
    )
    context['results'] = results 
    
    context['keyword'] = keyword
    context['message'] = 'param received'
    
    return render(request, 'home/search_page.html', context)


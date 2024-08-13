from django import template
from django.shortcuts import get_object_or_404

from ..models import LikeModel, DislikeModel, SavedPostsModel

register = template.Library()

@register.simple_tag
def is_liked(post, user):
    # its repetitive but this will still help
        
    try:
        post_filter = get_object_or_404(LikeModel, post=post)

        #print('post user likes: ', post_filter.users.filter(id=user.id).exists())
        if post_filter.users.filter(id=user.id).exists():
            return True
        
    except:
        
        return False 

@register.simple_tag
def is_disliked(post, user):
    
    try:
        post_filter = get_object_or_404(DislikeModel, post=post)

        #print('post user likes: ', post_filter.users.filter(id=user.id).exists())
        if post_filter.users.filter(id=user.id).exists():
            return True
        
    except:
        
        return False 

# the comment like and dislike will handle the highlited buttons.
# if user likes the comment, then the like button will be red, otherwise, the default color: black.
# same with dislike, if its disliked by the user, the button will be blue
@register.simple_tag
def commentLike(comment, user):
    
    try:
        comment_liked = get_object_or_404(LikeModel, comment=comment)
        if comment_liked.users.filter(id=user.id).exists():
            return True
    except:
        return False
    
@register.simple_tag
def commentDislike(comment, user):
    
    try:
        comment_disliked = get_object_or_404(DislikeModel, comment=comment)
        if comment_disliked.users.filter(id=user.id).exists():
            return True
    except:
        return False
    
# this will return the number of users that have liked and/or disliked the comment
@register.simple_tag
def getCommentVoteCount(comment, user, option):
    
    if option == 'like':
        try:
            comment = get_object_or_404(LikeModel, comment=comment)
            if comment.users.filter(id=user.id).exists():
                return comment.users.all().count()
            # without the else return, the value will display 'None' instead of 0, 
            # if there are users however, it will just exclude the current user if they liked the comment
            else:
                return comment.users.all().count()
        except: 
            return 0
        
    elif option == 'dislike':
        try:
            comment = get_object_or_404(DislikeModel, comment=comment)
            if comment.users.filter(id=user.id).exists():
                return comment.users.all().count()
            # without the else return, the value will display 'None' instead of 0, 
            # if there are users however, it will just exclude the current user if they liked the comment
            else:
                return comment.users.all().count()
        except: 
            return 0


@register.simple_tag
def is_saved(post, user):
    
    try:
        saved_post = get_object_or_404(SavedPostsModel, post__id=post)
        
        if saved_post.users.filter(id=user.id).exists():
            return True
        else:
            
            return False
    except:
        return False
        
        
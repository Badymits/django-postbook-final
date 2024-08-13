from django import forms

from .models import Post, Comment

class CreatePostForm(forms.ModelForm):
    
    class Meta:
        model = Post
        fields = ['title', 'body', 'image']
        
        
class UpdatePostForm(forms.ModelForm):
    
    class Meta:
        model = Post
        fields = ['title', 'body', 'image']
        
        
class CreateCommentForm(forms.ModelForm):
    
    class Meta:
        model = Comment
        fields = ['body', 'image']


class EditCommentForm(forms.ModelForm):
    
    class Meta:
        model = Comment
        fields = ['body']
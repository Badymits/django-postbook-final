from django.db import models
from django.conf import settings
from django.utils.text import slugify

# Create your models here.

# returns the objects that have not been deleted
# removes the necessary step to include is_deleted=False in each of our query (madami yun taena so this saves time)
class SoftDeleteManager(models.Manager):
    
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

# to keep track of the deleted comments. For the replies to retain in the template
class SoftDeleteModel(models.Model):
    
    is_deleted          = models.BooleanField(default=False)
    
    objects             = SoftDeleteManager() # for reverse relationships
    
    # as a replacement from the usual 'Model.objects.all() -> Model.all_objects.all()'
    # this will also include the objects that have been soft deleted
    all_objects         = models.Manager() 
    
    def soft_delete(self):
        self.is_deleted = True
        self.save()
        
    def restore(self):
        self.is_deleted = False
        self.save()

    class Meta:
        abstract = True

# create our models as subclasses of SoftDeleteModel to grant them the ability to be soft-deleted 
class Post(SoftDeleteModel):
    
    user                = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title               = models.CharField(max_length=255)
    body                = models.CharField(max_length=955, null=True, blank=True)
    date_posted         = models.DateTimeField(auto_now_add=True)
    image               = models.ImageField(upload_to='images', blank=True, null=True)
    slug                = models.SlugField(default="", max_length=255, blank=True, null=True)
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        return super().save(*args, **kwargs)
          
    def get_likes(self):
        try:
            post = self.post_likes.get(post=self.id)
            if self.user.user_likes.filter(users=self.user).exists():
                return post.users.all().count()
            
            # when users unliked an already liked post, 
            # this will just return the number of users (without loggedin user) that have liked the post
            else:
                return post.users.all().count()
        except:
            
            return 0 
       
    
    def get_dislikes(self):
        
        try:
            post = self.post_dislikes.get(post=self.id)
            if self.user.user_likes.filter(users=self.user).exists():
                return post.users.all().count()
            
            # when users unliked an already liked post, 
            # this will just return the number of users (without loggedin user) that have liked the post
            else:
                return post.users.all().count()
        except:
            
            return 0 

class Comment(SoftDeleteModel):
    
    main_post           = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    reply               = models.ForeignKey('Comment', default="", on_delete=models.SET_DEFAULT, null=True, related_name='replies') # to be used in a nested comment thread
    user                = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body                = models.CharField(max_length=955)
    image               = models.ImageField(default='images', blank=True, null=True)
    date_posted         = models.DateTimeField(auto_now_add=True, null=True)
    comment_level       = models.IntegerField(null=True, blank=True)
    is_edited           = models.BooleanField(default=False, null=True, blank=True)
    
    # override the __init__ method of models.Model so that you can keep a copy of the original value
    __original_name = None
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_name = self.body
        
    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        
        # making sure that the original value is not empty. 
        # The init method does not run when obj of a class is created despite it being a well known fact... at least for me
        if self.body != self.__original_name and self.__original_name != "":
            self.is_edited = True
        
        super().save(force_insert, force_update, *args, **kwargs) # Call the "real" save() method
        self.__original_name = self.body
            
    
    def __str__(self):
        return f'{self.user.first_name} replying to {self.main_post.title} content: {self.body}'
    
    # By making use of reply_id, we avoid loading the reply model object if it exists, which can lead to an N+1 problem
    @property
    def is_reply(self):
        return self.reply is not None
    
    @property
    def get_reply(self):
        return self.reply
    
    # if true, then we can identify if it is a nested comment or not.
    @property
    def has_replies(self):
        if self.is_deleted == True or self.is_deleted == False:
            return self.replies.exists()
        else:
            return self.replies.DoesNotExist
    
    # gets all replies related to the object that called it
    @property
    def get_replies(self):
        
        #  this will lead to an O(n) problem for larger scale comment threads
        replies = []
        for obj in Comment.all_objects.filter(main_post=self.main_post):
            if (obj.is_deleted or obj.is_deleted == False) and obj.reply == self:
                replies.append(obj)
        
        return replies
    
    
    def get_likes(self):
        
        try:
            comment = self.comment_likes.get(comment=self.id)
            if self.user.user_likes.filter(user=self.user).exists():
                
                return comment.users.all().count()
            
            else:
                return comment.users.all().count()
        except:
            return 0
        
    
    def get_dislikes(self):
        
        try:
            comment = self.comment_dislikes.get(comment=self.id)
            if self.user.user_likes.filter(user=self.user).exists():
                
                return comment.users.all().count()
            
            else:
                return comment.users.all().count()
        except:
            return 0
        
    # to retrieve comment user's profile photo
    @property
    def get_photo_url(self):
        
        if self.user.profile_pic and hasattr(self.user.profile_pic, 'url'):
            return self.user.profile_pic.url
        else:
            return "/static/images/profile/images/xianyun.jpg"
    
class LikeModel(SoftDeleteModel):
    
    users               = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='user_likes')
    post                = models.ForeignKey(Post, related_name='post_likes', null=True, blank=True, on_delete=models.SET_NULL)
    comment             = models.ForeignKey(Comment, related_name='comment_likes', null=True, blank=True, on_delete=models.SET_NULL)
    
    
    def __str__(self):
        if self.post:
            return f'liking post: {self.post.title}'
        elif self.comment:
            return f'liking comment: {self.comment.body}'
        else:
            return f'deleted post | comment'
    
class DislikeModel(SoftDeleteModel):
    
    users               = models.ManyToManyField(settings.AUTH_USER_MODEL)
    post                = models.ForeignKey(Post, related_name='post_dislikes', null=True, blank=True, on_delete=models.SET_NULL)
    comment             = models.ForeignKey(Comment, related_name='comment_dislikes', null=True, blank=True, on_delete=models.SET_NULL)
    
    def __str__(self):
        if self.post:
            return f'disliking post: {self.post.title}'
        elif self.comment:
            return f'disliking comment: {self.comment.body}'
        else:
            return f'deleted post | comment'
        

class SavedPostsModel(SoftDeleteModel):
    
    users               = models.ManyToManyField(settings.AUTH_USER_MODEL)
    post                = models.ForeignKey(Post, null=True, blank=True, on_delete=models.CASCADE)
    
    def __str__(self):
        return f'saved post: {self.post.title}'
    

class Notification(models.Model):
    
    sender              = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sender', null=True, blank=True)
    receiver            = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='receiver', null=True, blank=True)
    notif_type          = models.CharField(max_length=255, null=True, blank=True)
    is_read             = models.BooleanField(default=False, null=True, blank=True)
    message             = models.CharField(max_length=355, null=True, blank=True)
    date_added          = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.message
    
class Clients(models.Model):
    
    channel_name        = models.CharField(max_length=955, null=True, blank=True)
    
    
    
      
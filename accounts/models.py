from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Create your models here.
class MyAccountManager(BaseUserManager):
    
    def create_user(self, email, username, first_name, last_name, password=None):
        
        if not email:
            raise ValueError('Please enter email')
        
        if not username:
            raise ValueError('Please enter username')
        
        if not first_name:
            raise ValueError('Please enter first name')
        
        if not last_name:
            raise ValueError('Please eneter last name!')
        
        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            username=username
        )
        
        user.set_password(password)
        user.save(using=self.db)
        return user
            
    def create_superuser(self, email, username, first_name, last_name, password):
        
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password
        )
        
        user.is_admin       = True
        user.is_staff       = True
        user.is_superuser   = True
        
        user.save(using=self.db)
        return user
        
        

class Account(AbstractBaseUser, PermissionsMixin):
    
    email                   = models.EmailField(max_length=255, unique=True)
    username                = models.CharField(max_length=255, unique=True)
    bio                     = models.CharField(max_length=255, blank=True, null=True)
    first_name              = models.CharField(max_length=255, blank=True, null=True)
    last_name               = models.CharField(max_length=255, blank=True, null=True)
    date_joined             = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    profile_pic             = models.ImageField(upload_to='profile/images/', blank=True, null=True)
    banner_pic              = models.ImageField(upload_to='profile/images/', blank=True, null=True)
    
    is_admin                = models.BooleanField(default=False)
    is_active               = models.BooleanField(default=True)
    is_staff                = models.BooleanField(default=False)
    is_superuser            = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']
    objects = MyAccountManager()
    
    def __str__(self):
        
        return self.email
    
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return True
    
    
    @property
    def get_user_photo_url(self):
        
        if self.profile_pic and hasattr(self.profile_pic, 'url'):
            return self.profile_pic.url
        else:
            return "/static/images/profile/images/xianyun.jpg"
    
    @property
    def get_user_banner_url(self):
        
        if self.banner_pic and hasattr(self.banner_pic, 'url'):
            return self.banner_pic.url
        else:
            return "/static/images/images/furinalezgoooo.png"

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account
# Register your models here.

class AccountAdmin(UserAdmin):
    
    # which fields do we want to see as soon as we visit the list
    list_display = ('email', 'first_name', 'last_name', 'date_joined', 'last_login', 'is_admin', 'is_staff')
    
    # we want to search by email or firstname
    search_fields = ('email', 'first_name')
    
    # these are read only fields and cannot be changed
    readonly_fields = ('date_joined', 'last_login')
    
    filter_horizontal = ()
    list_filter = ()

    # it is important to put in fieldsets, if this is not included, then django would throw an error
    fieldsets = ()
    
admin.site.register(Account, AccountAdmin) # include model name, then admin class name
    


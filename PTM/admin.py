from django.contrib import admin
from django.contrib.auth.models import User

from .models import Meeting, MeetingNote,Allprojects,User

# admin.site.register(Project)
admin.site.register(Meeting)
admin.site.register(MeetingNote)
admin.site.register(Allprojects)
admin.site.register(User)

def activate_users(modeladmin, request, queryset):
    queryset.update(is_active=True)
activate_users.short_description = "Activate selected users"

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active')
    actions = [activate_users]

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
# admin.site.register(TaskDeadlineUpdateForm)



#from django.contrib import admin
# from .models import Profile
# Register your models here.
# admin.site.register(Profile)
#from .models import Project, Meeting
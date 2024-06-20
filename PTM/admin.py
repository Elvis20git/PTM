from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import Meeting, MeetingNote, Allprojects, CustomUser
from import_export.admin import ImportExportModelAdmin
from .models import MyModel
from .resources import MyModelResource


# Register your models here.
admin.site.register(Meeting)
admin.site.register(MeetingNote)
admin.site.register(Allprojects)

@admin.register(MyModel)
class MyModelAdmin(ImportExportModelAdmin):
    resource_class = MyModelResource

# Define a custom UserAdmin to handle CustomUser
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj=obj)
        # Add custom fields to the existing fieldsets
        custom_fieldsets = fieldsets + (
            ('Custom Fields', {
                'fields': ('first_name', 'last_name', 'account_activation'),
            }),
        )
        return custom_fieldsets

    def get_add_fieldsets(self, request, obj=None):
        # Get the default fieldsets from the parent class (UserAdmin)
        fieldsets = super().get_add_fieldsets(request, obj=obj)
        # Add custom fields to the default add_fieldsets
        custom_add_fieldsets = fieldsets + (
            ('Custom Fields', {
                'fields': ('first_name', 'last_name', 'email', 'account_activation'),
            }),
        )
        return custom_add_fieldsets

admin.site.register(CustomUser, CustomUserAdmin)

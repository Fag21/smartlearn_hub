from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False

class CustomUserAdmin(UserAdmin):
    inlines = [UserProfileInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_staff', 'is_active')
    list_filter = ('user_type', 'is_staff', 'is_active', 'date_joined')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'bio', 'profile_picture', 'date_of_birth', 
                      'phone_number', 'website', 'location', 'learning_goals',
                      'current_level', 'preferred_language', 'time_zone',
                      'twitter', 'linkedin', 'github')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'email', 'first_name', 'last_name')
        }),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'points', 'streak', 'daily_goal', 'total_study_time')
    list_filter = ('streak',)
    search_fields = ('user__username', 'user__email')

admin.site.register(User, CustomUserAdmin)
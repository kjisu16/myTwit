from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Post, Follow
# Register your models here.

class FollowAdmin(admin.ModelAdmin):
  list_display = ("id", "follower", "following")

admin.site.register(User, UserAdmin)
admin.site.register(Post)
admin.site.register(Follow, FollowAdmin)
#admin.site.register(Like)
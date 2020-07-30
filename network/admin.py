from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin

from .models import User, Post, Follow
# Register your models here.

class FollowAdmin(admin.ModelAdmin):
  list_display = ("id", "follower", "following")

class PostAdmin(admin.ModelAdmin):
  list_display = ("id", "content", "user", "created_on")

admin.site.register(User, UserAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Follow, FollowAdmin)
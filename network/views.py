from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import User, Post, Follow

from itertools import chain
import operator


def index(request):

  # New post by user
  if request.method == "POST":
    user = User.objects.get(pk=request.user.id)
    content = request.POST["content"]

    new_post = Post(content=content, user=user)
    new_post.save()

    return HttpResponseRedirect(reverse("index"))
  else:
    try:
      user = User.objects.get(pk=request.user.id)
    except User.DoesNotExist:
      return render(request, "network/index.html")
    
    # Get posts from followings + user
    followings = User.objects.filter(followers__follower=user)
    
    following_posts = Post.objects.filter(user__in=followings)
    user_posts = Post.objects.filter(user=user)
    display_posts = list(chain(following_posts, user_posts))
    sorted_display_posts = sorted(display_posts, key=operator.attrgetter('created_on'), reverse=True)

    return render(request, "network/index.html", {
      "posts": sorted_display_posts
    })

def like_post(request):
  user = User.objects.get(pk=request.user.id)

  if request.method == 'POST':
    post_id = request.POST.get('post_id')
    post = Post.objects.get(id=post_id)

    if user in post.liked.all():
      post.liked.remove(user)
    else:
      post.liked.add(user)

    like, created = Like.objects.get_or_create(user=user, post_id=post_id)

    """
    if not created:
      if like.value == 'Like':
        like.value = 'Unlike'
      else:
        like.value = 'Like'

    like.save()
    """

  return HttpResponse()

def post_serialized_view(request):
  data = list(Post.objects.values())
  return JsonResponse(data, safe=False)

def explore(request):

  # Get all posts except user's posts
  user = User.objects.get(pk=request.user.id)
  ex_user_posts = Post.objects.exclude(user=user).order_by('-created_on')

  return render(request, "network/explore.html", {
    "ex_user_posts": ex_user_posts
  })

def profile(request, username):

  follower_user = User.objects.get(pk=request.user.id)
  profile = User.objects.get(username=username)

  if request.method == "POST":
    if request.POST["follow"] == "Follow":
      Follow.objects.create(follower=follower_user, following=profile)

      return HttpResponseRedirect(reverse("profile", args=(username,)))
    elif request.POST["follow"] == "Unfollow":
      Follow.objects.filter(follower=follower_user, following=profile).delete()

      return HttpResponseRedirect(reverse("profile", args=(username,))) 

  else:
    user_posts = Post.objects.filter(user=profile).order_by('-created_on')
    follower_num = profile.followers.all().count()
    following_num = profile.following.all().count()

    # check if already following
    if Follow.objects.filter(follower=follower_user, following=profile).count() == 0:
      followed = False
    else:
      followed = True

    return render(request, "network/profile.html", {
      "profile": profile,
      "user_posts": user_posts,
      "follower_num": follower_num,
      "following_num": following_num,
      "followed": followed
    })


def login_view(request):
  if request.method == "POST":

      # Attempt to sign user in
      username = request.POST["username"]
      password = request.POST["password"]
      user = authenticate(request, username=username, password=password)

      # Check if authentication successful
      if user is not None:
          login(request, user)
          return HttpResponseRedirect(reverse("index"))
      else:
          return render(request, "network/login.html", {
              "message": "Invalid username and/or password."
          })
  else:
      return render(request, "network/login.html")


def logout_view(request):
  logout(request)
  return HttpResponseRedirect(reverse("index"))


def register(request):
  if request.method == "POST":
      username = request.POST["username"]
      email = request.POST["email"]

      # Ensure password matches confirmation
      password = request.POST["password"]
      confirmation = request.POST["confirmation"]
      if password != confirmation:
          return render(request, "network/register.html", {
              "message": "Passwords must match."
          })

      # Attempt to create new user
      try:
          user = User.objects.create_user(username, email, password)
          user.save()
      except IntegrityError:
          return render(request, "network/register.html", {
              "message": "Username already taken."
          })
      login(request, user)
      return HttpResponseRedirect(reverse("index"))
  else:
      return render(request, "network/register.html")

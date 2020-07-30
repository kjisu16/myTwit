from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db.models import Count
from django.core.paginator import Paginator

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
      return render(request, "network/login.html")
    
    # Get posts from followings + user
    followings = User.objects.filter(followers__follower=user)
    
    following_posts = Post.objects.filter(user__in=followings)
    user_posts = Post.objects.filter(user=user)
    display_posts = list(chain(following_posts, user_posts))
    sorted_display_posts = sorted(display_posts, key=operator.attrgetter('created_on'), reverse=True)

    # Pagination for infinite scroll
    paginator = Paginator(sorted_display_posts, 10)
    page = request.GET.get('page', 1)
    try:
      posts = paginator.page(page)
    except(EmptyPage, InvalidPage):
      posts = paginator.page(paginator.num_pages)

    # Get top 3 posts with most likes
    top_liked_posts = Post.objects.annotate(total_likes=Count('liked')).order_by('-total_likes')[:3]

    # Get top 3 most followed users
    top_followed_users = User.objects.annotate(total_follower=Count('followers')).order_by('-total_follower')[:3]

    return render(request, "network/index.html", {
      "posts": posts,
      "top_liked_posts": top_liked_posts,
      "top_followed_users": top_followed_users
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

  return HttpResponse()

def post_serialized_view(request):
  data = [p.to_dict() for p in Post.objects.all()]
  return JsonResponse(data, safe=False)

def explore(request):

  # Get all posts except user's posts
  user = User.objects.get(pk=request.user.id)
  ex_user_posts = Post.objects.exclude(user=user).order_by('-created_on')

  # Get top 3 posts with most likes
  top_liked_posts = Post.objects.annotate(total_likes=Count('liked')).order_by('-total_likes')[:3]

  # Get top 3 most followed users
  top_followed_users = User.objects.annotate(total_follower=Count('followers')).order_by('-total_follower')[:3]

  return render(request, "network/explore.html", {
    "ex_user_posts": ex_user_posts,
    "top_liked_posts": top_liked_posts,
    "top_followed_users": top_followed_users
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
      first_name = request.POST["firstname"]
      last_name = request.POST["lastname"]

      # Ensure password matches confirmation
      password = request.POST["password"]
      confirmation = request.POST["confirmation"]
      if password != confirmation:
          return render(request, "network/register.html", {
              "message": "Passwords must match."
          })

      # Attempt to create new user
      try:
          user = User.objects.create_user(username, email, password, first_name=first_name, last_name=last_name)
          user.save()
      except IntegrityError:
          return render(request, "network/register.html", {
              "message": "Username already taken."
          })
      login(request, user)
      return HttpResponseRedirect(reverse("index"))
  else:
      return render(request, "network/register.html")

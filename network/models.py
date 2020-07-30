from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.utils import timezone

from PIL import Image
from itertools import chain


class User(AbstractUser):
  profilepic = models.ImageField(default='avatar.png', blank=True)

  def __str__(self):
    return self.username

  def save(self, *args, **kwargs):
    super().save(*args, **kwargs)
    img = Image.open(self.profilepic.path)

    if img.height > 20 or img.weight > 20:
      output_size = (300,300)
      img.thumbnail(output_size)
      img.save(self.profilepic.path)

class Post(models.Model):
  content = models.CharField(max_length=200, blank=False)
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='creator')
  created_on = models.DateTimeField(auto_now_add=True)
  liked = models.ManyToManyField(settings.AUTH_USER_MODEL, default=None, blank=True, related_name='liked_users')

  def __str__(self):
    return str(self.content)

  def total_likes(self):
    return self.liked.all().count()
  
  def get_date(self):
    time = timezone.now()

    sameday = self.created_on.day == time.day
    samemonth = self.created_on.month == time.month
    sameyear = self.created_on.year == time.year

    if sameyear and samemonth and sameday:
      if self.created_on.hour == time.hour:
        return str(time.minute-self.created_on.minute) + " min ago"
      else:
        if time.hour-self.created_on.hour == 1:
          return "1 hour ago"
        else:
          return str(time.hour-self.created_on.hour) + " hours ago"
    elif sameyear and samemonth and not sameday:
      if time.day-self.created_on.day == 1:
        return "1 day ago"
      else:
        return str(time.day-self.created_on.day) + " days ago"
    elif sameyear and not samemonth:
        if time.month-self.created_on.month == 1:
          return "1 month ago"
        else:
          return str(time.month-self.created_on.month) + " months ago"
  
  def to_dict(instance):
    op = instance._meta
    data = {}
    for f in chain(op.concrete_fields, op.private_fields):
      data[f.name] = f.value_from_object(instance)
    for f in op.many_to_many:
      data[f.name] = len([i.id for i in f.value_from_object(instance)])
    return data
     

class Follow(models.Model):
  follower = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='following', on_delete=models.CASCADE)
  following = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='followers', on_delete=models.CASCADE)

  def __str__(self):
    return f"{self.folower} follows {self.following}"

  class Meta:
    unique_together = ('follower', 'following',)


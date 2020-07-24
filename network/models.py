from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models


class User(AbstractUser):
  pass

  def __str__(self):
    return self.username

class Post(models.Model):
  content = models.CharField(max_length=200, blank=False)
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='creator')
  created_on = models.DateTimeField(auto_now_add=True)
  liked = models.ManyToManyField(settings.AUTH_USER_MODEL, default=None, blank=True, related_name='liked_users')

  def __str__(self):
    return str(self.content)

"""
LIKE_CHOICES = (
  ('Like', 'Like'),
  ('Unlike', 'Unlike')
)

class Like(models.Model):
  post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='liked_post')
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='liked_user')
  value = models.CharField(choices=LIKE_CHOICES, default='Like', max_length=10)

  def __str__(self):
    return str(self.post)
"""

class Follow(models.Model):
  follower = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='following', on_delete=models.CASCADE)
  following = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='followers', on_delete=models.CASCADE)

  def __str__(self):
    return f"{self.folower} follows {self.following}"

  class Meta:
    unique_together = ('follower', 'following',)


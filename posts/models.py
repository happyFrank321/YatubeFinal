from django.db import models
from django.contrib.auth import get_user_model
from groups.models import Group


User = get_user_model()


class Post(models.Model):
    text = models.TextField(
        help_text="Текст поста(расскажите что-нибудь интересное)"
        )
    pub_date = models.DateTimeField(
        "date published",
        auto_now_add=True
        )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts"
        )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name="posts",
        blank=True,
        null=True,
        help_text='Группа(необязательное поле)'
        )
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        null=True
        )
     
    class Meta:
        ordering = ['-pub_date']
        
    def __str__(self):
        return self.text


class Comments(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created']


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")

from django import forms
from .models import Post, Comments
from django.forms import ModelForm


class CreatePost(ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']


class CreateComment(ModelForm):
    text = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Comments
        fields = ['text']
        
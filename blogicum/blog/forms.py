from django import forms
from django.contrib.auth import get_user_model

from .models import Post, Comment

User = get_user_model()


class PostForm(forms.ModelForm):

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['pub_date'].initial = timezone.localtime(
    #         timezone.now()
    #     ).strftime('%Y-%m-%dT%H-:%M')

    class Meta:
        model = Post
        fields = ('title', 'text', 'image', 'location', 'category', 'pub_date')
        widgets = {
            'pub_date': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={'type': 'datetime-local'}
            )
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',)

from django import forms
from .models import Contact, comment_put, Article


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'phone', 'body']



class CommentForm(forms.ModelForm):

        class Meta:
                model = comment_put
                fields =[
                 
                 'comment',
                 
                ]


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'image', 'body']
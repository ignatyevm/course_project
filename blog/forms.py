from django import forms
from .models import Comment, Post
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout


class FilterForm(forms.Form):
    filters = [('by_author', 'По автору'),
               ('by_content', 'По содержанию')]

    filter_name = forms.ChoiceField(choices=filters, widget=forms.RadioSelect, label='Выберите критерий поиска')
    keywords = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Ключевые слова'}), label='',
                               max_length=300,
                               required=True)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

    def form_valid(self, form, post):
        form.instance.author = self.request.user
        form.instance.post = post
        return super().form_valid(form)

    def save(self, author, post):
        comment = super(CommentForm, self).save(commit=False)
        comment.author = author
        comment.post = post
        comment.save()
        return comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'date', 'journal', 'volume', 'number', 'file']

    def save(self, author):
        post = super(PostForm, self).save(commit=False)
        post.author = author
        post.save()
        return post

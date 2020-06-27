from django import forms
from .models import Comment, Post
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout


class FilterForm(forms.Form):
    # filters = [('by_author', 'По автору'),
    #            ('by_content', 'По содержанию'),
    #            ('by_journal', 'По журналу'),
    #            ('by_org', 'По организации')]

    # filter_name = forms.ChoiceField(choices=filters, widget=forms.RadioSelect, label='Выберите критерий поиска')
    author = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Автор'}), label='',
                             max_length=300,
                             required=False)
    content = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Ключевые слова'}), label='',
                              max_length=300,
                              required=False)
    organization = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Организация'}), label='',
                                   max_length=150, required=False)
    journal = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Журнал'}), label='', max_length=100,
                              required=False)


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

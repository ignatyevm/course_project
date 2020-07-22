import re

from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, Comment
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from .forms import FilterForm, CommentForm, PostForm
from users.models import Profile, Organization
from django.db.models import Q


def home(request):
    posts = []
    if request.method == 'POST':
        filter_form = FilterForm(request.POST)
        if filter_form.is_valid():
            content = filter_form.cleaned_data.get('content').strip()
            author = filter_form.cleaned_data.get('author')
            organization = filter_form.cleaned_data.get('organization')
            journal = filter_form.cleaned_data.get('journal')
            if content:
                content = content.split('.')
                q = Q()
                for keyword in content:
                    q |= Q(title__icontains=keyword.lower())
                    q |= Q(content__icontains=keyword.lower())
                posts += Post.objects.all().filter(q).all()
            if author:
                author = author.split(' ')
                if len(author) == 1:
                    posts += Post.objects.filter(
                        Q(author__first_name__icontains=author[0]) | Q(author__last_name__icontains=author[0])).all()
                elif len(author) == 2:
                    posts += Post.objects.filter(
                        (Q(author__first_name__icontains=author[0]) & Q(author__last_name__icontains=author[1])) |
                        (Q(author__first_name__icontains=author[1]) & Q(author__last_name__icontains=author[0]))).all()
            if organization:
                posts += Post.objects.filter(author__profile__organization__name__icontains=organization).all()
            if journal:
                posts += Post.objects.filter(journal__icontains=journal).all()
    else:
        filter_form = FilterForm()
        all_posts = Post.objects.all().reverse()
        page = request.GET.get('page')
        paginator = Paginator(all_posts, 7)
        if page:
            posts = paginator.page(page)
        else:
            posts = paginator.page(1)

    for post in posts:
        cleanr = re.compile('<.*?>')
        post.content = re.sub(cleanr, '', post.content)
    return render(request, 'blog/home.html', {'posts': posts, 'filter': {'form': filter_form}})


class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    ordering = ['-date']


def view_posts(request, pk):
    author = Profile.objects.get(pk__exact=pk).user
    return render(request, 'blog/home.html', {'objects': author.post_set.all()})


def post_detail(request, pk=None):
    post = Post.objects.get(id__exact=pk)
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
        form = CommentForm(request.POST)
        if form.is_valid():
            form.save(request.user, post)
            return redirect('post-detail', pk)
    else:
        form = CommentForm()
    comments = post.comment_set.all()
    for comment in comments:
        cleanr = re.compile('<.*?>')
        comment.content = re.sub(cleanr, '', comment.content)
    return render(request, 'blog/post_detail.html', {
        'role': str(request.user.groups.first()), 'object': post, 'form': form, 'comments': comments, 'size': round(post.file.size / 2.0 ** 20, 2)
    })


def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})


def post_create(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(request.user)
            return redirect('blog-home')
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form})


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content', 'date', 'journal', 'volume', 'number']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content', 'date', 'journal', 'volume', 'number']
    template_name = 'blog/post_update.html'

    def form_valid(self, form):
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author or not self.request.user.profile.access == 'Пользователь':
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author or not self.request.user.profile.access == 'Пользователь':
            return True
        return False

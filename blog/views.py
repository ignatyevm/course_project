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
    posts = None
    if request.method == 'POST':
        filter_form = FilterForm(request.POST)
        if filter_form.is_valid():
            filter_name = filter_form.cleaned_data.get('filter_name')
            keywords = filter_form.cleaned_data.get('keywords').lower().split(' ')
            if filter_name == 'by_content':
                q = Q()
                for keyword in keywords:
                    q &= Q(title__icontains=keyword)
                    q &= Q(content__icontains=keyword)
                posts = Post.objects.all().filter(q)
            elif filter_name == 'by_author':
                q = Q()
                if len(keywords) == 1:
                    users = User.objects.all().filter(first_name=keywords[0])
                    for user in users:
                        print(user.first_name)
                        q |= Q(author=user)
                posts = Post.objects.all().filter(q)
            elif filter_name == 'by_org':
                q = Q()
                for keyword in keywords:
                    q &= Q(name__iexact=keyword)
                organizations = Organization.objects.all().filter(q)
                for org in organizations:
                    profiles = Profile.objects.get(organization__exact=org)
                    for profile in profiles:
                        user = User.objects.get(username__exact=profile)

            # title = filter_form.cleaned_data.get('title')
            # author = filter_form.cleaned_data.get('author')
            # organization = filter_form.cleaned_data.get('organization')
            # journal = filter_form.cleaned_data.get('journal')
            # keywords = filter_form.cleaned_data.get('keywords').split(' ')
            # all_posts = Post.objects.all()
            # posts = Post.objects.none()
            #
            # for keyword in keywords:
            #     posts.add(all_posts.filter(title__icontains=keyword))
            #     posts.add(all_posts.filter(content__icontains=keyword))
            #     posts.add(all_posts.filter(journal__icontains=keyword))
                # posts = posts.filter(content__icontains=keyword)
                # posts = posts.filter(journal__icontains=keyword)
            # try:
            # 	user = User.objects.get(username__exact=keyword.strip())
            # 	posts.union(posts.filter(author__exact=user))
            # except Exception:
            # 	pass
        # if title.strip():
        # 	posts = posts.filter(title__contains=title.strip())
        # if organization.strip():
        # 	posts = posts.filter(organization__contains=organization.strip())
        # if journal.strip():
        # 	posts = posts.filter(journal__contains=journal.strip())
        # if author.strip():
        # 	try:
        # 		user = User.objects.get(username__exact=author.strip())
        # 		posts = posts.filter(author__exact=user)
        # 	except Exception:
        # 		posts = []
    else:
        filter_form = FilterForm()
        all_posts = Post.objects.all()
        page = request.GET.get('page')
        paginator = Paginator(all_posts, 7)
        if page:
            posts = paginator.page(page)
        else:
            posts = paginator.page(1)

        for post in posts:
            cleanr = re.compile('<.*?>')
            post.content = re.sub(cleanr, '', post.content)


        author = None
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
    return render(request, 'blog/post_detail.html', {
        'object': post, 'form': form, 'comments': post.comment_set.all(), 'size': round(post.file.size / 2.0 ** 20, 2)
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

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.contrib import messages

from blog.models import Post
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, GrantForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.contrib.auth.models import User
from django.views.generic import CreateView, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from .models import Profile, Organization
from dal import autocomplete


def sign_up(request):
    if request.method == 'POST':
        uform = UserRegisterForm(request.POST)
        pform = ProfileUpdateForm(request.POST, request.FILES)
        if uform.is_valid() and pform.is_valid():
            user = uform.save()
            pform.save(user)
            username = uform.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')
            return redirect('login')
    else:
        uform = UserRegisterForm()
        pform = ProfileUpdateForm()
    return render(request, 'users/signup.html', {'uform': uform, 'pform': pform})


@login_required
def user_update_profile(request, pk):
    if str(request.user.groups.first()) != "Moderator" and not (request.user.id == pk):
        return HttpResponseForbidden()

    profile = Profile.objects.get(pk=pk)

    if request.method == 'POST':
        uform = UserUpdateForm(request.POST, instance=profile.user)
        pform = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if uform.is_valid() and pform.is_valid():
            user = uform.save(profile.user.username)
            pform.save(profile.user)
            messages.success(request, f'Account has been updated')
            return redirect('user-detail', profile.id)
    else:
        uform = UserUpdateForm(instance=profile.user)
        pform = ProfileUpdateForm(instance=profile)

    return render(request, 'users/profile_update.html', {'uform': uform, 'pform': pform, 'profile': profile})


@login_required
def admin_panel(request):
    if request.user.profile.access == 'admin':
        return render(request, 'users/admin_panel.html',
                      {'access': request.user.profile.access, 'users': User.objects.all()})
    else:
        return HttpResponseForbidden()


class UserDeleteView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, DeleteView):
    model = User
    template_name = 'users/user_confirm_delete.html'
    success_url = '/'
    success_message = 'User was deleted Successfully'

    def test_func(self):
        user = self.get_object()
        if self.request.user == user or self.request.user.profile.access == 'Администратор':
            return True
        return False

    def get_success_message(self, cleaned_data):
        return self.success_message


def user_detail(request, pk):
    profile = Profile.objects.get(id__exact=pk)
    return render(request, 'users/profile_detail.html', {'object': profile, 'grants': profile.grant_set.all()})


def grant_add(request, pk):
    profile = request.user.profile
    if str(request.user.groups.first()) != "Moderator" and not (request.user.id == pk):
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = GrantForm(request.POST)
        if form.is_valid():
            form.save(profile)
            return redirect('user-detail', profile.id)
    else:
        form = GrantForm()
    return render(request, 'users/grant_add.html', {'profile': Profile.objects.get(pk=pk), 'form': form})


class OrganizationAutocomplete(autocomplete.Select2QuerySetView):
     def get_queryset(self):
        orgs = Organization.objects.all()
        
        if self.q:
            orgs = orgs.filter(name__istartswith=self.q)

        return orgs


class OrganizationCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Organization
    fields = ['name', 'date', 'constitutors', 'address', 'link', 'description']
    
    def test_func(self):
        if not self.request.user.profile.access == 'Пользователь':
            return True
        return False


class OrganizationDetailView(DetailView):
    model = Organization


def organization_detail(request, pk):
    try:
        organization = Organization.objects.get(id=pk)
        organization_posts = Post.objects.all().filter(author__profile__organization_id=pk).filter(has_moderated=True).reverse()
        return render(request, 'users/organization_detail.html', {'object': organization, 'posts': organization_posts})
    except ObjectDoesNotExist:
        return HttpResponseNotFound()


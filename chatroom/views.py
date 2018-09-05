from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.core.urlresolvers import reverse

from .models import Room, Message
from django.contrib.auth.models import User

from .forms import RoomForm, MessageForm, UserForm, UploadFile
from django.contrib.auth.forms import UserCreationForm

from django.views.generic import View, ListView, DetailView
from django.views.generic.edit import FormMixin, CreateView, DeleteView, UpdateView
from django.views.generic.list import BaseListView
from django.views.generic.detail import SingleObjectMixin

from django.core.exceptions import PermissionDenied


class RoomList(ListView):
    def get_user(self):
        return User.objects.get(username=self.request.user.username)

    def get_queryset(self):
        queryset = Room.objects.all()
        if not self.get_user().is_superuser:
            queryset = self.get_user().rooms.all()
        return queryset


class RoomDetail(FormMixin, DetailView):
    model = Room
    form_class = MessageForm

    def get_message_queryset(self):
        qs = self.get_object().messages.all()
        last = self.request.GET.get('last',0)
        if last:
            qs = qs.filter(pk__gt=last)
        return qs

    def get_success_url(self):
        return reverse('chatroom:room-detail', kwargs={'slug':self.get_object().slug})

    def get_context_data(self, **kwargs):
        context = super(RoomDetail, self).get_context_data(**kwargs)
        context['form'] = self.get_form()
        context['message'] = self.get_message_queryset()
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.room = Room.objects.get(slug=self.kwargs['slug'])
        form.save()
        return super(RoomDetail, self).form_valid(form)

    def get_template_names(self):
        template_names = super(RoomDetail, self).get_template_names()
        if self.request.is_ajax():
            template_names = 'chatroom/message.html'
        return template_names

    def dispatch(self, request, *args, **kwargs):
        members = self.get_object().members.all()
        if not request.user.is_superuser:
            if request.user not in members:
                raise PermissionDenied()
        return super(RoomDetail, self).dispatch(request, *args, **kwargs)


class RoomSettings(UpdateView):
    model = Room
    form_class = RoomForm


class CreateRoom(CreateView):
    model = Room
    form_class = RoomForm


class DeleteRoom(DeleteView):
    model = Room

    def get(self, request, *args, **kwargs):
        return self.post(self, request, *args, **kwargs)

    def get_success_url(self):
        return reverse('chatroom:room-list')


class MemberList(ListView):
    def get_template_names(self):
        template_names = 'chatroom/member_list.html'
        return template_names

    def get_not_members(self):
        qs = User.objects.exclude(rooms__slug__contains=self.kwargs['slug'])
        return qs.filter(is_superuser=False)

    def get_context_data(self, **kwargs):
        context = super(MemberList, self).get_context_data(**kwargs)
        context['not_members'] = self.get_not_members()
        context['room'] = self.get_room()
        return context

    def get_room(self):
        return Room.objects.get(slug=self.kwargs['slug'])

    def get_queryset(self):
        return self.get_room().members.exclude(username=self.request.user.username)


class AddMemberToRoom(SingleObjectMixin, View):
    model = User

    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponseForbidden
        user = self.get_object()
        room = Room.objects.get(slug=self.kwargs['slug'])
        room.members.add(user)
        room.save()
        return HttpResponseRedirect(reverse('chatroom:room-detail',
                                            kwargs={'slug':self.kwargs['slug']}))


class RemoveMemberFromRoom(SingleObjectMixin, View):
    model = User

    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponseForbidden
        user = self.get_object()
        room = Room.objects.get(slug=self.kwargs['slug'])
        room.members.remove(user)
        room.save()
        return HttpResponseRedirect(reverse('chatroom:room-detail',
                                            kwargs={'slug':self.kwargs['slug']}))


class UserManager(FormMixin, ListView):
    form_class = UploadFile


    def get_queryset(self):
        return User.objects.filter(is_superuser=False)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied()
        return super(UserManager, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('chatroom:user-manager')

    def get_context_data(self, **kwargs):
        context = super(UserManager, self).get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context

    def handle_uploaded_file(self, upload_file):
        for line in upload_file:
            for i, char in enumerate(line, 1):
                if char == " ":
                    username = line[:i].rstrip()
                    password = line[i+1:].strip()
                    break
            if User.objects.filter(username=username).exists():
                pass
            else:
                user = User.objects.create_user(username=username)
                user.set_password(password)
                user.save()

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            self.handle_uploaded_file(request.FILES['file'])
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class DeleteUser(DeleteView):
    model = User

    def get(self, request, *args, **kwargs):
        return self.post(self, request, *args, **kwargs)

    def get_success_url(self):
        return reverse('chatroom:user-manager')


class CreateUser(CreateView):
    model = User
    form_class = UserForm

    def get_success_url(self):
        return reverse('chatroom:user-manager')



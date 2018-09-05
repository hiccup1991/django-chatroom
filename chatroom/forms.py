from django import forms
from django.contrib.auth.models import User
from .models import Room, Message

from django.utils.translation import ugettext, ugettext_lazy as _


class RoomForm(forms.ModelForm):
    name = forms.CharField(
        label=_("Name"),
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_superuser=False),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=False,
    )


    class Meta:
        model = Room
        fields = ('name', 'members')

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(RoomForm, self).__init__(*args, **kwargs)


class MessageForm(forms.ModelForm):
    content = forms.CharField(
        label=_("Content"),
        widget=forms.Textarea(attrs={'class': 'form-control input-chat',
                                     'rows': 3})
    )

    class Meta:
        model = Message
        fields = ('content',)

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(MessageForm, self).__init__(*args, **kwargs)


class UserForm(forms.ModelForm):
    username = forms.CharField(
        label=_("Username"),
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = User
        fields = ('username', 'password')

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(UserForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        user = super(UserForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UploadFile(forms.Form):
    file = forms.FileField(
        label=_("Upload File To Create User"),
        widget=forms.FileInput(attrs={'class': 'form-contorl'}),
    )


from django.conf.urls import url, include
from django.contrib.auth.views import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test

from .views import RoomDetail, RoomList, RoomSettings
from .views import CreateRoom, DeleteRoom
from .views import MemberList, AddMemberToRoom, RemoveMemberFromRoom
from .views import UserManager, CreateUser, DeleteUser


app_name = 'chatroom'
urlpatterns = [
    url(r'^$',
        login_required(RoomList.as_view()),
        name='room-list'),
    url(r'^rooms/createroom/$',
        user_passes_test(lambda u: u.is_superuser)(CreateRoom.as_view()),
        name='create-room'),
    url(r'^rooms/deleteroom/(?P<slug>[-\w]+)/$',
        user_passes_test(lambda u: u.is_superuser)(DeleteRoom.as_view()),
        name='delete-room'),
    url(r'^(?P<slug>[-\w]+)/$',
        login_required(RoomDetail.as_view()),
        name='room-detail'),
    url(r'^(?P<slug>[-\w]+)/settings/$',
        user_passes_test(lambda u: u.is_superuser)(RoomSettings.as_view()),
        name='room-settings'),


    url(r'^(?P<slug>[-\w]+)/members/$',
        login_required(MemberList.as_view()),
        name='member-list'),
    url(r'^(?P<slug>[-\w]+)/addmember/(?P<pk>[\d]+)/$',
        user_passes_test(lambda u: u.is_superuser)(AddMemberToRoom.as_view()),
        name='add-member'),
    url(r'^(?P<slug>[-\w]+)/removemember/(?P<pk>[\d]+)/$',
        user_passes_test(lambda u: u.is_superuser)(RemoveMemberFromRoom.as_view()),
        name='remove-member'),


    url(r'^accounts/login/$', 
        login,
       ),
    url(r'^accounts/logout/$',
        logout,
        {'next_page': '/'},
        name='logout'),

    url(r'^accounts/usermanager/$',
        login_required(UserManager.as_view()),
        name='user-manager'),
    url(r'^accounts/createuser/$',
        user_passes_test(lambda u: u.is_superuser)(CreateUser.as_view()),
        name='create-user'),
    url(r'^accounts/deleteuser/(?P<pk>[\d]+)/$',
        user_passes_test(lambda u: u.is_superuser)(DeleteUser.as_view()),
        name='delete-user'),
]

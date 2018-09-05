from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify


class Room(models.Model):
    name = models.CharField(max_length=40, unique=True)
    slug = models.SlugField()
    members = models.ManyToManyField(User,
                                     related_name="rooms",
                                     limit_choices_to={'is_superuser':False},
                                    )

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Room, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('chatroom:room-detail', kwargs={"slug": self.slug})



class Message(models.Model):
    room = models.ForeignKey(Room, related_name="messages")
    user = models.ForeignKey(User)

    content = models.CharField(max_length=250)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']


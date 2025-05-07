from django.contrib import admin

from .models import CustomUser, Post, Comment, Notification, Message,GamingClip, Service,GameUpload

# Register your models here.
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Notification)
admin.site.register(Message)
admin.site.register(CustomUser)
admin.site.register(GamingClip)
admin.site.register(Service)
admin.site.register(GameUpload)

from django.contrib import admin

from django.contrib.admin import ModelAdmin, site
from .models import MessageModel, DialogsModel


class MessagModelAdmin(ModelAdmin):
    readonly_fields = ('created', 'modified',)
    search_profile = ('id', 'text', 'sender__pk', 'recipient__pk')
    list_display = ('id', 'sender', 'recipient', 'text', 'file', 'read')
    list_display_links = ('id',)
    list_filter = ('sender', 'recipient')
    date_hierarchy = 'created'


class DialogsModelAdmin(ModelAdmin):
    readonly_fields = ('created', 'modified')
    search_fields = ('id', 'user1__pk', 'user2__pk')
    list_display = ('id', 'user1', 'user2')
    lost_display_links = ('id')
    date_hierarchy = 'created'


site.register(DialogsModel, DialogsModelAdmin)
site.register(MessageModel, MessagModelAdmin)

from django.contrib import admin
from django.template.response import TemplateResponse

from unfold.admin import ModelAdmin
from .models import Chat, Message
from apps.authentication.models import User


class ChatAdmin(ModelAdmin):
    change_list_template = 'admin/custom_admin.html'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        users = User.objects.filter(is_superuser=False)
        admin_user = User.objects.filter(is_superuser=True).first()
        chats = Chat.objects.filter(admin=admin_user)

        extra_context['users'] = users
        extra_context['chats'] = chats
        extra_context['admin_id'] = admin_user.id if admin_user else None
        return TemplateResponse(request, self.change_list_template, extra_context)


admin.site.register(Chat, ChatAdmin)
admin.site.register(Message)

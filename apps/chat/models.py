from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Chat(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Пользователь"), related_name='chats')
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name=_("Админ"), related_name='admin_chats')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))

    def __str__(self):
        return f"Чат с {self.user}"

    class Meta:
        verbose_name = _('Чат')
        verbose_name_plural = _("Чаты")


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages', verbose_name=_("Чат"))
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Отправитель"), related_name='sent_messages')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Получатель"),
                                  related_name='received_messages')
    content = models.TextField(verbose_name=_("Сообщение"), blank=True)
    image = models.ImageField(upload_to='message_images/', null=True, blank=True, verbose_name=_("Изображение"))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата отправки"))
    is_read = models.BooleanField(default=False, verbose_name=_("Прочитано"))

    def __str__(self):
        return f"Сообщение от {self.sender} в чате {self.chat}"

    class Meta:
        verbose_name = _('Сообщения')
        verbose_name_plural = _("Сообщении")

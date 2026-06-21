# chat_service/admin.py
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from .models import ChatRoomAudit, MessageAudit
from chat_service.models import ChatRoom, Message  # seus modelos originais

# ─── Admins para CRUD Events ──────────────────────────────
class ChatRoomAuditAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'user', 'datetime', 'object_repr')
    list_filter = ('event_type', 'user', 'datetime')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        content_type = ContentType.objects.get_for_model(ChatRoom)
        return qs.filter(content_type=content_type)

class MessageAuditAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'user', 'datetime', 'object_repr')
    list_filter = ('event_type', 'user', 'datetime')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        content_type = ContentType.objects.get_for_model(Message)
        return qs.filter(content_type=content_type)

admin.site.register(ChatRoomAudit, ChatRoomAuditAdmin)
admin.site.register(MessageAudit, MessageAuditAdmin)

from django.contrib import admin
from chat_service.models import ChatRoom, Message   # seus modelos originais

class MessageInline(admin.TabularInline):   # ou admin.StackedInline, se preferir visualização vertical
    model = Message
    extra = 0                               # não exibe linhas vazias extras para novos registros
    fields = ('usuario_id', 'conteudo', 'data_envio')
    readonly_fields = ('data_envio',)       # a data de envio é automática, não deve ser editada
    can_delete = True
    show_change_link = True

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('carona_id', 'criado_em', 'ativo', 'mensagens_count')
    list_filter = ('ativo', 'criado_em')
    search_fields = ('carona_id',)
    inlines = [MessageInline]

    def mensagens_count(self, obj):
        return obj.mensagens.count()
    mensagens_count.short_description = 'Qtd. Mensagens'
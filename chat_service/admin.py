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

# ─── Admins para os Modelos Originais ─────────────────────

class MessageInline(admin.TabularInline):   
    model = Message
    extra = 0                               
    fields = ('usuario', 'conteudo', 'data_envio')  # Atualizado para o relacionamento
    readonly_fields = ('data_envio',)       
    can_delete = True
    show_change_link = True

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('carona_id', 'criado_em', 'ativo', 'mensagens_count')
    list_filter = ('ativo', 'criado_em')
    search_fields = ('carona_id',)
    
    # RESOLUÇÃO DO ERRO: Comentado para o Admin ignorar o formulário de mensagens por enquanto
    # inlines = [MessageInline]

    def mensagens_count(self, obj):
        # Um try/except seguro para evitar que a contagem quebre se a relação tiver outro nome
        try:
            return obj.mensagens.count()
        except AttributeError:
            return 0
    mensagens_count.short_description = 'Qtd. Mensagens'
from django.contrib import admin

from api.models import EmailTemplate, EmailTrigger, EmailLog


__all__ = ['EmailTemplateAdmin', 'EmailTriggerAdmin', 'EmailLogAdmin']


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'date_created')
    search_fields = ('name', 'subject')
    list_filter = ('date_created',)
    ordering = ('-date_created',)

@admin.register(EmailTrigger)
class EmailTriggerAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'template', 'date_created')
    search_fields = ('event_type',)
    list_filter = ('event_type', 'date_created',)
    ordering = ('-date_created',)

@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'user', 'email_template', 'status', 'sent_at')
    search_fields = ('event_type', 'user__email', 'email_template__name', 'status')
    list_filter = ('status', 'sent_at')
    ordering = ('-sent_at',)
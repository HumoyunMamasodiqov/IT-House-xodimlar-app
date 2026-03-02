from django.contrib import admin
from .models import *

@admin.register(BonusSabab)
class BonusSababAdmin(admin.ModelAdmin):
    list_display = ['nom', 'pul_miqdori', 'ball_miqdori', 'active', 'created_at']
    list_filter = ['active']
    search_fields = ['nom']
    list_editable = ['pul_miqdori', 'ball_miqdori', 'active']

@admin.register(JarimaSabab)
class JarimaSababAdmin(admin.ModelAdmin):
    list_display = ['nom', 'pul_miqdori', 'ball_miqdori', 'active', 'created_at']
    list_filter = ['active']
    search_fields = ['nom']
    list_editable = ['pul_miqdori', 'ball_miqdori', 'active']

@admin.register(Xodim)
class XodimAdmin(admin.ModelAdmin):
    list_display = ['ism', 'familya', 'telefon', 'bonus_ball', 'jarima_ball', 'reyting_ball', 'reyting_pul']
    list_filter = ['user__is_active']
    search_fields = ['ism', 'familya', 'telefon']
    readonly_fields = ['bonus_ball', 'bonus_pul', 'jarima_ball', 'jarima_pul', 'reyting_ball', 'reyting_pul', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Shaxsiy ma\'lumotlar', {
            'fields': ('user', 'ism', 'familya', 'telefon')
        }),
        ('Statistika', {
            'fields': ('bonus_ball', 'bonus_pul', 'jarima_ball', 'jarima_pul', 'reyting_ball', 'reyting_pul')
        }),
        ('Vaqt', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(BonusRecord)
class BonusRecordAdmin(admin.ModelAdmin):
    list_display = ['xodim', 'sabab', 'pul_miqdori', 'ball_miqdori', 'sana', 'created_by']
    list_filter = ['sana', 'sabab']
    search_fields = ['xodim__ism', 'xodim__familya', 'izoh']
    date_hierarchy = 'sana'
    readonly_fields = ['sana']
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(JarimaRecord)
class JarimaRecordAdmin(admin.ModelAdmin):
    list_display = ['xodim', 'sabab', 'pul_miqdori', 'ball_miqdori', 'sana', 'created_by']
    list_filter = ['sana', 'sabab']
    search_fields = ['xodim__ism', 'xodim__familya', 'izoh']
    date_hierarchy = 'sana'
    readonly_fields = ['sana']
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Reyting)
class ReytingAdmin(admin.ModelAdmin):
    list_display = ['xodim', 'davr', 'reyting_ball', 'reyting_pul', 'sana']
    list_filter = ['davr', 'sana']
    search_fields = ['xodim__ism', 'xodim__familya']
    date_hierarchy = 'sana'
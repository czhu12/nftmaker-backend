from django.contrib import admin
from community.models import Community, Message, Contract, CommunalCanvas, Pixel


class CommunityAdmin(admin.ModelAdmin):
    list_display = ('name',)


class CommunalCanvasAdmin(admin.ModelAdmin):
    list_display = ('modified',)


class PixelAdmin(admin.ModelAdmin):
    list_display = ('token_identifier', 'modified')


class ContractAdmin(admin.ModelAdmin):
    list_display = ('name',)


class MessageAdmin(admin.ModelAdmin):
    list_display = ('token_identifier', 'body')


admin.site.register(Community, CommunityAdmin)
admin.site.register(CommunalCanvas, CommunalCanvasAdmin)
admin.site.register(Pixel, PixelAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Contract, ContractAdmin)

from django.contrib import admin
from editor.models import Group, Asset, Layer, Project


# Register your models here.
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name',)


class AssetAdmin(admin.ModelAdmin):
    list_display = ('name',)


class LayerAdmin(admin.ModelAdmin):
    list_display = ('name',)


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name',)


admin.site.register(Group, GroupAdmin)
admin.site.register(Asset, AssetAdmin)
admin.site.register(Layer, LayerAdmin)
admin.site.register(Project, ProjectAdmin)

from django.contrib import admin
from .models import Pokemon, PokemonType, DataRun


@admin.register(Pokemon)
class PokemonAdmin(admin.ModelAdmin):
    list_display = ('name', 'primary_type', 'hp')
    search_fields = ('name',)
    list_filter = ('primary_type',)


@admin.register(PokemonType)
class PokemonTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(DataRun)
class DataRunAdmin(admin.ModelAdmin):
    list_display = ('source', 'created_at')
    list_filter = ('source',)

from django.contrib import admin

from .models import Disciplina, Duvida


@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nome', 'ativa']
    list_filter = ['ativa']
    search_fields = ['codigo', 'nome']
    filter_horizontal = ['monitores']


@admin.register(Duvida)
class DuvidaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'disciplina', 'autor', 'monitor_responsavel', 'situacao', 'criada_em']
    list_filter = ['situacao', 'disciplina']
    search_fields = ['titulo', 'descricao']
    readonly_fields = ['criada_em', 'atualizada_em']
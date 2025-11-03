from django.contrib import admin
from .models import Project, PresetParameters, Experiment, Result


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'creation_date')
    search_fields = ('name', 'description')
    list_filter = ('creation_date',)


@admin.register(PresetParameters)
class PresetParametersAdmin(admin.ModelAdmin):
    list_display = ('name', 'creation_date', 'modification_date')
    search_fields = ('name', 'description')
    list_filter = ('creation_date',)


@admin.register(Experiment)
class ExperimentAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'state', 'creation_date')
    list_filter = ('state', 'creation_date', 'project')
    search_fields = ('name', 'notes')
    readonly_fields = (
        'celery_task_id',
        'creation_date',
        'processing_start_time',
        'processing_end_time'
    )


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('experiment', 'generation_date')
    search_fields = ('experiment__name',)
    readonly_fields = ('generation_date',)

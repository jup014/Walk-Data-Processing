from django.contrib import admin

from walk_data_processing.admin import DeleteAllAdmin

from .models import TaskLog




@admin.action(description='Delete all TaskLogs')
def delete_all_tasklogs(modeladmin, request, queryset):
    TaskLog.objects.all().delete()

class TaskLogAdmin(DeleteAllAdmin):
    readonly_fields = ('when_created', 'msg',)
    actions = [delete_all_tasklogs]

delete_all_tasklogs.acts_on_all=True
admin.site.register(TaskLog, TaskLogAdmin)
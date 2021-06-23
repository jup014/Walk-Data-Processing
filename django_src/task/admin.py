from django.contrib import admin

# Register your models here.

from .models import Task


@admin.action(description='Delete all Tasks')
def delete_all_tasks(modeladmin, request, queryset):
    Task.objects.all().delete()

class TaskAdmin(admin.ModelAdmin):
    readonly_fields = ('pkey', 'function_name', 'params', 'status', 'when_created', 'depends',)
    actions = [delete_all_tasks]
    
    def changelist_view(self, request, extra_context=None):
        try:
            action = self.get_actions(request)[request.POST['action']][0]
            action_acts_on_all = action.acts_on_all
        except (KeyError, AttributeError):
            action_acts_on_all = False

        if action_acts_on_all:
            post = request.POST.copy()
            post.setlist(admin.helpers.ACTION_CHECKBOX_NAME,
                        self.model.objects.values_list('id', flat=True))
            request.POST = post

        return admin.ModelAdmin.changelist_view(self, request, extra_context)

delete_all_tasks.acts_on_all=True
admin.site.register(Task, TaskAdmin)
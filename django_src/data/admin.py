from django.contrib import admin

# Register your models here.

from .models import RawSteps


@admin.action(description='Delete all RawSteps')
def delete_all_raw_steps(modeladmin, request, queryset):
    RawSteps.objects.all().delete()

class RawStepsAdmin(admin.ModelAdmin):
    fields = ['local_datetime', 'local_date', 'local_time', 'user_id', 'steps']
    actions = [delete_all_raw_steps]
    
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

delete_all_raw_steps.acts_on_all=True
admin.site.register(RawSteps, RawStepsAdmin)
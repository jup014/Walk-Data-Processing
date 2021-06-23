from django.contrib import admin

from walk_data_processing.admin import DeleteAllAdmin

from .models import RawSteps
from .models import Padded_Steps


@admin.action(description='Delete all RawSteps')
def delete_all_raw_steps(modeladmin, request, queryset):
    RawSteps.objects.all().delete()

class RawStepsAdmin(DeleteAllAdmin):
    fields = ['local_datetime', 'local_date', 'local_time', 'user_id', 'steps']
    actions = [delete_all_raw_steps]

delete_all_raw_steps.acts_on_all=True
admin.site.register(RawSteps, RawStepsAdmin)



@admin.action(description='Delete all PaddedSteps')
def delete_all_padded_steps(modeladmin, request, queryset):
    Padded_Steps.objects.all().delete()

class PaddedStepsAdmin(DeleteAllAdmin):
    fields = ['local_datetime', 'local_date', 'local_time', 'user_id', 'steps']
    actions = [delete_all_padded_steps]

delete_all_padded_steps.acts_on_all=True
admin.site.register(Padded_Steps, PaddedStepsAdmin)
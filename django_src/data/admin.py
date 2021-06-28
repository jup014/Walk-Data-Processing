from django.contrib import admin

from walk_data_processing.admin import DeleteAllAdmin

from .models import RawSteps
from .models import Padded_Steps
from .models import BinaryWalked
from .models import AverageWalked
from .models import BinaryWalked2
from .models import ThreeHour



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



@admin.action(description='Delete all BinaryWalked')
def delete_all_binary_walked(modeladmin, request, queryset):
    BinaryWalked.objects.all().delete()

class BinaryWalkedAdmin(DeleteAllAdmin):
    fields = ['local_datetime', 'local_date', 'local_time', 'user_id', 'did_walked']
    actions = [delete_all_binary_walked]

delete_all_binary_walked.acts_on_all=True
admin.site.register(BinaryWalked, BinaryWalkedAdmin)



@admin.action(description='Delete all AverageWalked')
def delete_all_average_walked(modeladmin, request, queryset):
    AverageWalked.objects.all().delete()

class AverageWalkedAdmin(DeleteAllAdmin):
    fields = ['local_datetime', 'local_date', 'local_time', 'user_id', 'mean_did_walked', 'window_size']
    actions = [delete_all_average_walked]

delete_all_average_walked.acts_on_all=True
admin.site.register(AverageWalked, AverageWalkedAdmin)



@admin.action(description='Delete all BinaryWalked2')
def delete_all_binary_walked2(modeladmin, request, queryset):
    BinaryWalked2.objects.all().delete()

class BinaryWalked2Admin(DeleteAllAdmin):
    fields = ['local_datetime', 'local_date', 'local_time', 'user_id', 'did_walked', 'window_size', 'threshold1']
    actions = [delete_all_binary_walked2]

delete_all_binary_walked2.acts_on_all=True
admin.site.register(BinaryWalked2, BinaryWalked2Admin)





class ThreeHourAdmin(DeleteAllAdmin):
    fields = ['user_id', 
              'local_date', 
              'step', 
              'window_size', 
              'threshold1',
              'index_three_hour',
              'did_walked', ]
    
admin.site.register(ThreeHour, ThreeHourAdmin)

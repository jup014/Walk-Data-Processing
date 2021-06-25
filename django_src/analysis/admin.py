from django.contrib import admin

from walk_data_processing.admin import DeleteAllAdmin

from .models import Aggregated1


class Aggregated1Admin(DeleteAllAdmin):
    fields = ['index_day', 'index_method', 'key_n_days', 'key_window_size', 'key_threshold1', 'key_threshold2', 'TP', 'TN', 'FP', 'FN']

admin.site.register(Aggregated1, Aggregated1Admin)

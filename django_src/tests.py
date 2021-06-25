
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'walk_data_processing.settings')

import django
django.setup()


from task.tasks.analysis import load_data

load_data(1)
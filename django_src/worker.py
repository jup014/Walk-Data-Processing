import os
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'walk_data_processing.settings'
django.setup()


import pprint
from data.models import RawSteps


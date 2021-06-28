
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'walk_data_processing.settings')

import django
django.setup()

import pprint

# from task.tasks.analysis import load_data
from task.tasks.preprocessing import minute_padding2
# load_data(1)
from datetime import datetime
from data.models import RawSteps

user_obj = RawSteps.objects.first()

# minute_padding2(48, datetime(2016, 1, 11))
# minute_padding2(user_obj.user_id, user_obj.local_date)

user_list = RawSteps.objects.distinct('user_id', 'local_date')
        
is_testing = False
index = 0
for user_obj in user_list:        
    
    print({
            "user_id": user_obj.user_id,
            "local_date": user_obj.local_datetime.date()
        })
    # pprint.pprint(user_obj.__dict__)
    if is_testing == True and index > 3:
        break
    index += 1
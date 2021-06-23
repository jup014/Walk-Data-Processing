from django.db.models import Sum

from task.models import TaskLog

from data.models import RawSteps
from data.models import Padded_Steps

from datetime import datetime, timedelta
import pytz
import json
import pprint
import math

def minute_padding(args):
    TaskLog.log("minute_padding: {}".format(args))
    
    args_dict = json.loads(args)

    user_id = args_dict['user_id']
    local_date = datetime.strptime(args_dict['local_date'], '%Y-%m-%d').astimezone(pytz.utc)
    
    obj_list = RawSteps.objects.filter(
        user_id=user_id, 
        local_date=local_date).values(
            'user_id', 
            'local_datetime', 
            'local_date', 
            'local_time').annotate(steps2=Sum('steps'))
    
    padded_list = [0] * 1440
    
    for obj in obj_list:
        local_time = obj["local_time"]
        list_index = local_time.hour * 60 + local_time.minute
        padded_list[list_index] += obj["steps2"]
        
    padded_steps_list = []
    
    for i in range(0, 1440):
        local_datetime = local_date + timedelta(hours=math.floor(i/60), minutes=(i%60))
        padded_steps_list.append(Padded_Steps(
            local_datetime=local_datetime,
            user_id=user_id,
            steps=padded_list[i],
            local_date=local_date,
            local_time=local_datetime.time()
        ))
    
    Padded_Steps.objects.bulk_create(padded_steps_list)
from django.db.models import Sum

from task.models import TaskLog

from data.models import RawSteps

from datetime import datetime
import json
import pprint

def minute_padding(args):
    TaskLog.log("minute_padding: {}".format(args))
    
    print(args)
    args_dict = json.loads(args)

    user_id = args_dict['user_id']
    local_date = datetime.strptime(args_dict['local_date'], '%Y-%m-%d')
    
    obj_list = RawSteps.objects.filter(
        user_id=user_id, 
        local_date=local_date).values(
            'user_id', 
            'local_datetime', 
            'local_date', 
            'local_time').annotate(steps2=Sum('steps'))
    
    pprint.pprint(obj_list)
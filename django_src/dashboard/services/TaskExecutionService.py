from django.db import IntegrityError, transaction

from data.models import RawSteps, Padded_Steps, BinaryWalked, \
    AverageWalked

from task.models import TaskLog

from task.tasks import minute_padding

import pprint
import json

class TaskExecutionService:
    def execute(self):
        user_list = RawSteps.objects.distinct('user_id')
        
        is_testing = False
        index = 0
        for user_obj in user_list:        
            minute_padding.apply_async(
                kwargs={
                    'args': {
                        "user_id": user_obj.user_id
                    }
                }
            )
            if is_testing == True and index > 3:
                break
            index += 1
        
        return "submitted"
    
    def reset(self):
        Padded_Steps.objects.all().delete()
        BinaryWalked.objects.all().delete()
        AverageWalked.objects.all().delete()
        TaskLog.objects.all().delete()
        
        return "Database is cleared."
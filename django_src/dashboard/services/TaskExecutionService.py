from django.db import IntegrityError, transaction

from data.models import RawSteps, Padded_Steps, BinaryWalked, \
    AverageWalked, BinaryWalked2
from analysis.models import Aggregated1

from task.models import TaskLog

from task.tasks import minute_padding, aggregate2, load_data

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
        Aggregated1.objects.all().delete()
        BinaryWalked2.objects.all().delete()
        Padded_Steps.objects.all().delete()
        BinaryWalked.objects.all().delete()
        AverageWalked.objects.all().delete()
        TaskLog.objects.all().delete()
        
        return "Database is cleared."
    
    def load_data(self):
        user_list = RawSteps.objects.distinct('user_id')
        
        is_testing = False
        index = 0
        for user_obj in user_list:        
            load_data.apply_async(
                kwargs={
                    'user_id': user_obj.user_id
                }
            )
            if is_testing == True and index > 3:
                break
            index += 1
        
        return "submitted"
    
    def aggr(self):
        aggregate2.apply_async(
            kwargs={}
        )
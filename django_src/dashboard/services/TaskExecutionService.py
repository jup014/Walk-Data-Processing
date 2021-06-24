from django.db import IntegrityError, transaction

from data.models import RawSteps
from task.models import TaskLog

from task.tasks import minute_padding

import pprint
import json

class TaskExecutionService:
    def execute(self):
        user_list = RawSteps.objects.distinct('user_id')
        
        for user_obj in user_list:        
            minute_padding.apply_async(
                kwargs={
                    'args': {
                        "user_id": user_obj.user_id
                    }
                }
            )
        
        return "submitted"
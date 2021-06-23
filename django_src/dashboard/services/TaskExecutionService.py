from data.models import RawSteps
from task.models import Task

import pprint
import json

class TaskExecutionService:
    def execute(self):
        user_list = RawSteps.objects.distinct('user_id', "local_date")
                
        task_list = []
        for user_obj in user_list:
            param_dict = {"user_id": user_obj.user_id,
                          "local_date": user_obj.local_date.strftime("%Y-%m-%d")
                          }
            Task.objects.create(function_name='task.tasks.minute_padding',
                    params=json.dumps(param_dict)
                    )

        return "submitted"
from data.models import RawSteps
from task.models import Task

import pprint

class TaskExecutionService:
    def execute(self):
        user_list = RawSteps.objects.distinct('user_id', "local_date")
                
        task_list = []
        for user_obj in user_list:
            Task.objects.create(function_name='task.tasks.minute_padding',
                    params={'user_id': user_obj.user_id,
                            'local_date': user_obj.local_date
                            }
                    )

        return "submitted"
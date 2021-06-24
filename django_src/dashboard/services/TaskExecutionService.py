from django.db import IntegrityError, transaction

from data.models import RawSteps
from task.models import Task, TaskLog

import pprint
import json

class TaskExecutionService:
    def execute(self):
        user_list = RawSteps.objects.distinct('user_id')
                
        task_list = []
        for user_obj in user_list:
            try:
                with transaction.atomic():
                    binarize_param_dict = {
                        "user_id": user_obj.user_id
                    }
                    
                    binarize_task = Task.objects.create(
                        function_name='task.tasks.binarize',
                        params=json.dumps(binarize_param_dict)
                        )
                    
                    user_date_list = RawSteps.objects.filter(
                        user_id=user_obj.user_id
                    ).distinct('local_date')

                    for user_date_obj in user_date_list:
                        padding_param_dict = {
                            "user_id": user_obj.user_id,
                            "local_date": user_date_obj.local_date.strftime("%Y-%m-%d")
                        }
                        
                        padding_task = Task.objects.create(
                            function_name='task.tasks.minute_padding',
                            params=json.dumps(padding_param_dict)
                            )
                        
                        binarize_task.depends.add(padding_task)
                        
                    binarize_task.save()
            except IntegrityError as e:
                TaskLog.log(e)

        return "submitted"
from django.db import IntegrityError, transaction
from django.db.models import Q

from task.models import Task
from task.models import TaskLog

class TaskFetcherService:
    def get_next_task(self):
        try:
            with transaction.atomic():
                task_obj = Task.objects.filter(Q(status=0), Q(depends=None) | Q(depends__status=3)).order_by('-when_created').first()
                if task_obj:
                    task_obj.status = 1
                    task_obj.save()
        except IntegrityError as e:
            TaskLog.log(e)
            print(e)
        
        return task_obj